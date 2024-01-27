"""Support for Hydrao ble sensors."""
from __future__ import annotations

import logging

from .Hydrao import HydraoDevice

from homeassistant import config_entries
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfElectricPotential,
    CONDUCTIVITY,
    VOLUME   
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import DOMAIN, WATER_VOLUME

_LOGGER = logging.getLogger(__name__)

SENSORS_MAPPING_TEMPLATE: dict[str, SensorEntityDescription] = {
    "current_volume": SensorEntityDescription(
        key="current_volume",
        name="Current shower volume",
        force_update=True,
        native_unit_of_measurement=WATER_VOLUME,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:shower-head",
    ),
    "total_volume": SensorEntityDescription(
        key="total_volume",
        name="Total shower volume",
        native_unit_of_measurement=WATER_VOLUME,
        force_update=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:shower-head",
    ),
    "current_temperature": SensorEntityDescription(
        key="current_temperature",
        name="Current temperature",
        force_update=True,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-water",
        suggested_display_precision=1,
    ),
    "average_temperature": SensorEntityDescription(
        key="average_temperature",
        name="Average temperature",
        force_update=True,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-water",
        suggested_display_precision=1,
    ),
    "current_duration": SensorEntityDescription(
        key="current_duration",
        name="Current duration",
        force_update=True,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-outline",
        suggested_display_precision=1,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Hydrao BLE sensors."""
    is_metric = hass.config.units is METRIC_SYSTEM

    coordinator: DataUpdateCoordinator[HydraoDevice] = hass.data[DOMAIN][entry.entry_id]
    sensors_mapping = SENSORS_MAPPING_TEMPLATE.copy()
    entities = []
    _LOGGER.debug("got sensors: %s", coordinator.data.sensors)
    for sensor_type, sensor_value in coordinator.data.sensors.items():
        if sensor_type not in sensors_mapping:
            _LOGGER.debug(
                "Unknown sensor type detected: %s, %s",
                sensor_type,
                sensor_value,
            )
            continue
        entities.append(
            HydraoSensor(coordinator, coordinator.data, sensors_mapping[sensor_type])
        )

    async_add_entities(entities)


class HydraoSensor(CoordinatorEntity[DataUpdateCoordinator[HydraoDevice]], SensorEntity):
    """Hydrao BLE sensors for the device."""

    #_attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        hydrao_device: HydraoDevice,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Populate the Hydrao entity with relevant data."""
        super().__init__(coordinator)
        self.entity_description = entity_description

        name = f"{hydrao_device.name} {hydrao_device.identifier}"

        self._attr_unique_id = f"{name}_{entity_description.key}"

        self._id = hydrao_device.address
        self._attr_device_info = DeviceInfo(
            connections={
                (
                    CONNECTION_BLUETOOTH,
                    hydrao_device.address,
                )
            },
            name=name,
            manufacturer="Hydrao",
            model="Aloe",
            hw_version=hydrao_device.hw_version,
            sw_version=hydrao_device.sw_version,
        )
        _LOGGER.debug("Created Sensor: %s", entity_description.key)

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        try:
            return self.coordinator.data.sensors[self.entity_description.key]
        except KeyError:
            return None