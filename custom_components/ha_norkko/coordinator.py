"""DataUpdateCoordinator for ha_norkko."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HaNorkkoApiClientError

if TYPE_CHECKING:
    from .data import HaNorkkoConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class HaNorkkoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: HaNorkkoConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except HaNorkkoApiClientError as exception:
            raise UpdateFailed(exception) from exception
