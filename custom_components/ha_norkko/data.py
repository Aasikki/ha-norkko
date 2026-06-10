"""Custom types for ha_norkko."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import HaNorkkoApiClient
    from .coordinator import HaNorkkoDataUpdateCoordinator


type HaNorkkoConfigEntry = ConfigEntry[HaNorkkoData]


@dataclass
class HaNorkkoData:
    """Data for the ha_norkko integration."""

    client: HaNorkkoApiClient
    coordinator: HaNorkkoDataUpdateCoordinator
    integration: Integration
