from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities(
        [
            CecotecAvailableBinarySensor(coordinator),
            CecotecConnectedBinarySensor(coordinator),
        ]
    )

class CecotecBaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Youngdo/Cecotec humidifier binary sensor base class"""

    _attr_should_poll = False

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info

class CecotecAvailableBinarySensor(CecotecBaseBinarySensor):
    """Youngdo/Cecotec humidifier bluetooth available sensor"""

    _attr_translation_key = "humidifier_available_binary_sensor"
    _attr_has_entity_name = True

    def __init__(self, coordinator):
      super().__init__(coordinator)
      self.coordinator = coordinator
      self._attr_unique_id = f"{self.coordinator.address}_available"
      self._attr_icon = "mdi:bluetooth"

    @property
    def is_on(self) -> bool:
        return self.coordinator.is_available


class CecotecConnectedBinarySensor(CecotecBaseBinarySensor):
    """Youngdo/Cecotec humidifier bluetooth connected sensor"""

    _attr_translation_key = "humidifier_connected_binary_sensor"
    _attr_has_entity_name = True

    def __init__(self, coordinator):
      super().__init__(coordinator)
      self.coordinator = coordinator
      self._attr_unique_id = f"{self.coordinator.address}_connected"
      self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool:
        return self.coordinator.is_connected
