"""Entity base class for ha_norkko."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import HaNorkkoDataUpdateCoordinator


class HaNorkkoEntity(CoordinatorEntity[HaNorkkoDataUpdateCoordinator]):
    """Base entity for ha_norkko."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: HaNorkkoDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        )
