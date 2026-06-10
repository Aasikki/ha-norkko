"""Norkko API client."""

from __future__ import annotations

import asyncio
import re
import socket
from typing import Any

import aiohttp
import async_timeout

from .const import DATA_URL, DEFAULT_POLLEN_ORDER, LOGGER


class HaNorkkoApiClientError(Exception):
    """Exception to indicate a general API error."""


class HaNorkkoApiClientCommunicationError(HaNorkkoApiClientError):
    """Exception to indicate a communication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    response.raise_for_status()


class HaNorkkoApiClient:
    """Norkko feed API client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize API client."""
        self._session = session

    async def async_get_data(self) -> dict[str, Any]:
        """Get parsed data from the Norkko text feed."""
        raw_text = await self._api_wrapper(method="get", url=DATA_URL)
        return self._parse_feed(raw_text)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> str:
        """Request text data from the feed."""
        try:
            LOGGER.debug("Starting fetch from %s with 60s timeout", url)
            async with async_timeout.timeout(60):
                LOGGER.debug("Timeout context entered, making request...")
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                LOGGER.debug("Request completed, status %s", response.status)
                _verify_response_or_raise(response)
                LOGGER.debug("Reading response text...")
                raw_text = await response.text()
                LOGGER.debug("Successfully fetched %d bytes from Norkko", len(raw_text))
                return raw_text

        except asyncio.TimeoutError as exception:
            msg = f"Timeout error fetching Norkko data - asyncio timeout after 60s: {exception}"
            LOGGER.error(msg)
            raise HaNorkkoApiClientCommunicationError(msg) from exception
        except TimeoutError as exception:
            msg = f"Timeout error fetching Norkko data - timeout: {exception}"
            LOGGER.error(msg)
            raise HaNorkkoApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = (
                f"Error fetching Norkko data - {type(exception).__name__}: {exception}"
            )
            LOGGER.error(msg)
            raise HaNorkkoApiClientCommunicationError(msg) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Unexpected error fetching Norkko data - {type(exception).__name__}: {exception}"
            LOGGER.error(msg)
            raise HaNorkkoApiClientError(msg) from exception

    @staticmethod
    def _parse_feed(raw_text: str) -> dict[str, Any]:
        """Parse the Norkko text feed into structured data."""
        lines = [line.strip() for line in raw_text.splitlines()]
        if not lines:
            raise HaNorkkoApiClientError("Feed returned empty response")

        uppercase = [line.upper() for line in lines]
        try:
            tilanne_index = uppercase.index("TILANNE")
            ennuste_index = uppercase.index("ENNUSTE", tilanne_index + 1)
        except ValueError as exception:
            raise HaNorkkoApiClientError(
                "Unable to locate TILANNE or ENNUSTE in feed"
            ) from exception

        current_section = lines[tilanne_index + 1 : ennuste_index]
        forecast_section = []
        for line in lines[ennuste_index + 1 :]:
            if not line:
                continue
            upper_line = line.upper()
            if (
                upper_line.startswith("TUNNUKSET")
                or upper_line.startswith("ASTEIKK")
                or upper_line.startswith("(TEKSTIT)")
                or upper_line.startswith("KERÄYSPA")
            ):
                break
            forecast_section.append(line)

        current_date = ""
        if current_section and re.match(r"^\d{2}\.\d{2}\.\d{4}$", current_section[0]):
            current_date = current_section[0]
            current_section = current_section[1:]

        forecast_period = ""
        if forecast_section and re.match(
            r"^\d{2}\.\d{2}\.\d{4}\s*-\s*\d{2}\.\d{2}\.\d{4}$", forecast_section[0]
        ):
            forecast_period = forecast_section[0]
            forecast_section = forecast_section[1:]

        pollen_codes = HaNorkkoApiClient._parse_pollen_codes(lines)
        current = HaNorkkoApiClient._parse_location_rows(current_section)
        forecast = HaNorkkoApiClient._parse_location_rows(forecast_section)
        locations = sorted(set(current) | set(forecast))

        current = HaNorkkoApiClient._fill_missing_codes(current, pollen_codes)
        forecast = HaNorkkoApiClient._fill_missing_codes(forecast, pollen_codes)

        return {
            "current_date": current_date,
            "forecast_period": forecast_period,
            "locations": locations,
            "current": current,
            "forecast": forecast,
            "pollen_codes": pollen_codes,
        }

    @staticmethod
    def _parse_pollen_codes(lines: list[str]) -> list[str]:
        """Extract pollen codes from the feed legend."""
        for line in lines:
            if line.upper().startswith("TUNNUKSET"):
                matches = re.findall(r"[^,]+\s+([A-Za-z])", line)
                if matches:
                    return [code.upper() for code in matches]
        return DEFAULT_POLLEN_ORDER

    @staticmethod
    def _parse_location_rows(rows: list[str]) -> dict[str, dict[str, int]]:
        """Parse location rows into code severity values."""
        locations: dict[str, dict[str, int]] = {}
        for line in rows:
            if (
                not line
                or line.upper().startswith("TUNNUKSET")
                or line.upper().startswith("ASTEIKK")
            ):
                continue
            parsed = HaNorkkoApiClient._parse_location_line(line)
            if not parsed:
                continue
            location, codes = parsed
            locations[location] = codes
        return locations

    @staticmethod
    def _parse_location_line(line: str) -> tuple[str, dict[str, int]] | None:
        """Parse a single location/codes row."""
        match = re.match(r"^(.+?)\s+([A-Za-z,\s]+)$", line)
        if not match:
            return None

        location = match.group(1).strip()
        code_text = match.group(2)
        code_groups = re.findall(r"[A-Za-z]+", code_text)
        codes: dict[str, int] = {}
        for group in code_groups:
            code = group[0].upper()
            severity = len(group)
            if severity > codes.get(code, 0):
                codes[code] = min(severity, 3)
        return location, codes

    @staticmethod
    def _fill_missing_codes(
        locations: dict[str, dict[str, int]], pollen_codes: list[str]
    ) -> dict[str, dict[str, int]]:
        """Ensure every location has all expected pollen codes."""
        for location, codes in locations.items():
            for code in pollen_codes:
                codes.setdefault(code, 0)
        return locations
