"""Sensor platform for the Transelectrica SEN integration."""

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    API_KEY_TIMESTAMP,
    API_KEY_CONSUMPTION,
    API_KEY_PRODUCTION,
    API_KEY_EXCHANGE_BALANCE,
    INTERCONNECTION_KEYS,
)
from .coordinator import TranselectricaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Device class mapping
DEVICE_CLASS_MAP = {
    "power": SensorDeviceClass.POWER,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Transelectrica SEN sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []

    # Create a sensor for each defined sensor type
    for api_key, sensor_config in SENSOR_TYPES.items():
        entities.append(
            TranselectricaSensor(
                coordinator=coordinator,
                entry=entry,
                api_key=api_key,
                sensor_config=sensor_config,
            )
        )

    # Add the grid renewable percentage sensor (computed)
    entities.append(
        TranselectricaRenewablePercentSensor(
            coordinator=coordinator,
            entry=entry,
        )
    )

    async_add_entities(entities)


class TranselectricaSensor(
    CoordinatorEntity[TranselectricaDataUpdateCoordinator], SensorEntity
):
    """Representation of a Transelectrica SEN sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TranselectricaDataUpdateCoordinator,
        entry: ConfigEntry,
        api_key: str,
        sensor_config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._api_key = api_key
        self._sensor_config = sensor_config
        self._attr_unique_id = f"{entry.entry_id}_{api_key}"
        self._attr_name = sensor_config["name"]
        self._attr_icon = sensor_config["icon"]
        self._attr_native_unit_of_measurement = sensor_config["unit"]
        self._attr_state_class = SensorStateClass.MEASUREMENT

        device_class_str = sensor_config.get("device_class")
        if device_class_str and device_class_str in DEVICE_CLASS_MAP:
            self._attr_device_class = DEVICE_CLASS_MAP[device_class_str]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info for the SEN grid."""
        return {
            "identifiers": {(DOMAIN, "sen_romania")},
            "name": "Romanian National Energy System (SEN)",
            "manufacturer": "Transelectrica",
            "model": "SEN Real-Time Monitor",
            "entry_type": "service",
            "configuration_url": "https://www.transelectrica.ro",
        }

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._api_key)
        if value is None:
            return None
        try:
            return round(float(value), 1)
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data is None:
            return attrs

        # Add timestamp
        timestamp = self.coordinator.data.get(API_KEY_TIMESTAMP)
        if timestamp:
            attrs["data_timestamp"] = timestamp

        # Add 15-minute average if available
        avg_15_key = self._sensor_config.get("avg_15_key")
        if avg_15_key:
            avg_val = self.coordinator.data.get(avg_15_key)
            if avg_val is not None:
                try:
                    attrs["average_15min"] = round(float(avg_val), 1)
                except (ValueError, TypeError):
                    pass

        # For exchange balance, add interconnection details
        if self._api_key == API_KEY_EXCHANGE_BALANCE:
            interconnections = {}
            for ic_key, ic_name in INTERCONNECTION_KEYS.items():
                ic_val = self.coordinator.data.get(ic_key)
                if ic_val is not None:
                    try:
                        interconnections[ic_name] = round(float(ic_val), 1)
                    except (ValueError, TypeError):
                        pass
            if interconnections:
                attrs["interconnections"] = interconnections

        # For production, add percentage breakdown
        if self._api_key == API_KEY_PRODUCTION:
            production = self.coordinator.data.get(API_KEY_PRODUCTION)
            if production:
                try:
                    prod_val = float(production)
                    if prod_val > 0:
                        from .const import (
                            API_KEY_COAL,
                            API_KEY_HYDROCARBONS,
                            API_KEY_HYDRO,
                            API_KEY_NUCLEAR,
                            API_KEY_WIND,
                            API_KEY_SOLAR,
                            API_KEY_BIOMASS,
                            API_KEY_STORAGE,
                        )

                        sources = {
                            "coal_pct": API_KEY_COAL,
                            "hydrocarbons_pct": API_KEY_HYDROCARBONS,
                            "hydro_pct": API_KEY_HYDRO,
                            "nuclear_pct": API_KEY_NUCLEAR,
                            "wind_pct": API_KEY_WIND,
                            "solar_pct": API_KEY_SOLAR,
                            "biomass_pct": API_KEY_BIOMASS,
                            "storage_pct": API_KEY_STORAGE,
                        }
                        for attr_name, src_key in sources.items():
                            src_val = self.coordinator.data.get(src_key)
                            if src_val is not None:
                                try:
                                    attrs[attr_name] = round(
                                        float(src_val) / prod_val * 100, 1
                                    )
                                except (ValueError, TypeError, ZeroDivisionError):
                                    pass
                except (ValueError, TypeError):
                    pass

        return attrs


class TranselectricaRenewablePercentSensor(
    CoordinatorEntity[TranselectricaDataUpdateCoordinator], SensorEntity
):
    """Sensor showing the percentage of renewable energy in the grid."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TranselectricaDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the renewable percentage sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_renewable_pct"
        self._attr_name = "Renewable Energy Percentage"
        self._attr_icon = "mdi:leaf-circle"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info for the SEN grid."""
        return {
            "identifiers": {(DOMAIN, "sen_romania")},
            "name": "Romanian National Energy System (SEN)",
            "manufacturer": "Transelectrica",
            "model": "SEN Real-Time Monitor",
            "entry_type": "service",
            "configuration_url": "https://www.transelectrica.ro",
        }

    @property
    def native_value(self) -> float | None:
        """Return the renewable energy percentage.

        Renewable = Hydro + Wind + Solar + Biomass
        Total = Production
        """
        if self.coordinator.data is None:
            return None

        from .const import (
            API_KEY_HYDRO,
            API_KEY_WIND,
            API_KEY_SOLAR,
            API_KEY_BIOMASS,
        )

        production = self.coordinator.data.get(API_KEY_PRODUCTION)
        if not production:
            return None

        try:
            prod_val = float(production)
            if prod_val <= 0:
                return None

            renewable = 0.0
            for key in (API_KEY_HYDRO, API_KEY_WIND, API_KEY_SOLAR, API_KEY_BIOMASS):
                val = self.coordinator.data.get(key)
                if val is not None:
                    renewable += max(float(val), 0)

            return round(renewable / prod_val * 100, 1)
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        attrs = {}
        if self.coordinator.data is None:
            return attrs

        timestamp = self.coordinator.data.get(API_KEY_TIMESTAMP)
        if timestamp:
            attrs["data_timestamp"] = timestamp

        return attrs
