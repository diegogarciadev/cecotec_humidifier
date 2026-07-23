import logging
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from .coordinator import BLECoordinator
from .const import DOMAIN
from datetime import datetime, timedelta


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up sensors for Cecotec Humidifier from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    # Lista de sensores a crear
    sensors = [
        #HumidifierStatusSensor(coordinator),
        HumidifierTimerRemainingSensor(coordinator),
    ]

    async_add_entities(sensors)
    return True

class HumidifierTimerRemainingSensor(CoordinatorEntity, SensorEntity):
    """Youngdo/Cecotec humidifier remaining timer data"""

    _attr_translation_key = "humidifier_remaining_timer"
    _attr_has_entity_name = True

    def __init__(self, coordinator: BLECoordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_remaining_timer"
        self._attr_icon = "mdi:timer"
        #self._attr_name = "Temporizador restante"
        self._attr_native_unit_of_measurement = "min"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info

    @property
    #def state(self):
    def native_value(self):
        return self.coordinator._remaining_timer_minutes

    @property
    def extra_state_attributes(self):
        minutes = self.coordinator._remaining_timer_minutes
        hours = minutes // 60
        mins = minutes % 60
        end_time = datetime.now() + timedelta(minutes=minutes)
        return {
            "formatted": f"{hours}h {mins}m",
            "end_time": end_time.isoformat(),
        }

class HumidifierStatusSensor(CoordinatorEntity, SensorEntity):
    _attr_translation_key = "humidifier_status"
    _attr_has_entity_name = True
    def __init__(self, coordinator: BLECoordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_humidifier_status"

    @property
    def device_info(self):
        return self.coordinator.device_info

    @property
    def native_value(self):
        #return self._state
        if self.coordinator.is_connected:
            return "Conected"
        else:
            return "Disconnected"
        #return self.coordinator.data["status"] #= value

    async def async_added_to_hass(self):
        """Subscribirse a notificaciones al añadir la entidad."""
        def callback(sender, data: bytearray):
            # Aquí transformas los datos recibidos en estado legible
            self._state = int.from_bytes(data, "little")
            self.async_write_ha_state()

    async def async_will_remove_from_hass(self):
      await self.coordinator.client.stop_notify(self.uuid_notify)
