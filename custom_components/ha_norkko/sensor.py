"""Sensor platform for ha_norkko."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity

from .const import POLLEN_TYPE_NAMES, SEVERITY_NAMES
from .entity import HaNorkkoEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import HaNorkkoDataUpdateCoordinator
    from .data import HaNorkkoConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: HaNorkkoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    location = entry.data["location"]
    pollen_codes = entry.runtime_data.coordinator.data.get(
        "pollen_codes", list(POLLEN_TYPE_NAMES)
    )

    entities = []
    for code in pollen_codes:
        entities.append(
            HaNorkkoSensor(
                coordinator=entry.runtime_data.coordinator,
                location=location,
                code=code,
                forecast=False,
            )
        )
        entities.append(
            HaNorkkoSensor(
                coordinator=entry.runtime_data.coordinator,
                location=location,
                code=code,
                forecast=True,
            )
        )

    async_add_entities(entities)


class HaNorkkoSensor(HaNorkkoEntity, SensorEntity):
    """ha_norkko sensor class."""

    def __init__(
        self,
        coordinator: HaNorkkoDataUpdateCoordinator,
        location: str,
        code: str,
        forecast: bool,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.location = location
        self.code = code
        self.forecast = forecast
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{'forecast' if forecast else 'current'}_{code}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        pollen_name = POLLEN_TYPE_NAMES.get(self.code, self.code)
        if self.forecast:
            return f"Pollen forecast {pollen_name} ({self.location})"
        return f"Pollen situation {pollen_name} ({self.location})"

    @property
    def native_value(self) -> str | None:
        """Return the value of the pollen sensor."""
        data = self.coordinator.data
        section = data["forecast"] if self.forecast else data["current"]
        severity = section.get(self.location, {}).get(self.code, 0)
        severity_text = SEVERITY_NAMES.get(severity, "none")
        if self.forecast:
            period = data.get("forecast_period", "")
            if not period:
                return severity_text
            return f"{period}: {severity_text}"
        return severity_text

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Return extra state attributes."""
        data = self.coordinator.data
        return {
            "location": self.location,
            "pollen_type": POLLEN_TYPE_NAMES.get(self.code, self.code),
            "forecast": str(self.forecast).lower(),
            "current_date": data.get("current_date"),
            "forecast_period": data.get("forecast_period"),
        }
