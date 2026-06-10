"""Adds config flow for ha_norkko."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LOCATION
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import HaNorkkoApiClient, HaNorkkoApiClientCommunicationError
from .const import DOMAIN, LOGGER


class HaNorkkoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for ha_norkko."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        locations = []

        try:
            locations = await self._async_fetch_locations()
        except HaNorkkoApiClientCommunicationError as exception:
            LOGGER.error("Unable to fetch Norkko locations: %s", exception)
            errors["base"] = "connection"

        if user_input is not None and not errors:
            await self.async_set_unique_id(user_input[CONF_LOCATION])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_LOCATION],
                data={CONF_LOCATION: user_input[CONF_LOCATION]},
            )

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        assert integration.documentation is not None, (  # noqa: S101
            "Integration documentation URL is not set in manifest.json"
        )

        return self.async_show_form(
            step_id="user",
            description_placeholders={
                "documentation_url": integration.documentation,
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LOCATION,
                        default=(user_input or {}).get(CONF_LOCATION),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                {"label": location, "value": location}
                                for location in locations
                            ],
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def _async_fetch_locations(self) -> list[str]:
        client = HaNorkkoApiClient(session=async_create_clientsession(self.hass))
        data = await client.async_get_data()
        return data["locations"]
