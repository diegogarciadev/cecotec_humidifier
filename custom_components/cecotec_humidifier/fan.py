import logging
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import BLECoordinator
from .const import DOMAIN, DEVICE_FAN_MODES, DEVICE_DEFAULT_FAN_MODE, DEVICE_FAN_MODE_LOW, DEVICE_FAN_MODE_MEDIUM, DEVICE_FAN_MODE_HIGH

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: BLECoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        CecotecHumidifierFan(coordinator)
    ])

class CecotecHumidifierFan(CoordinatorEntity, FanEntity):
    """Youngdo/Cecotec humidifier fan control"""

    _attr_translation_key = "humidifier_fan"
    _attr_has_entity_name = True
    _attr_supported_features = FanEntityFeature.PRESET_MODE | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_preset_modes = DEVICE_FAN_MODES

    def __init__(self, coordinator: BLECoordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_fan"

    @property
    def is_on(self) -> bool:
        return self.coordinator._fan_on

    @property
    def available(self) -> bool:
        return self.coordinator.is_available and self.coordinator.is_connected
    
    @property
    def preset_mode(self):
        return self.coordinator._preset_mode

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info

    async def async_turn_on(self, speed: str = None, percentage: int = None, preset_mode: str = None, **kwargs):
        self.coordinator._fan_on = True
        self.coordinator.update_state()
        await self.coordinator.send_command(bytes.fromhex("AAF10100000000000000FF73"))

    async def async_turn_off(self, **kwargs):
        self.coordinator._timer_hours = None
        self.coordinator._fan_on = False
        self.coordinator._preset_mode = DEVICE_DEFAULT_FAN_MODE
        self.coordinator._timer_hours = None
        self.coordinator._remaining_timer_minutes = 0
        #Set continuous mode before power off
        if not self.coordinator._continuous:
            await self.coordinator.send_command(bytes.fromhex("AAF30100000000000000FF73"))
            self.coordinator._continuous = True
        self.coordinator.update_state()
        await self.coordinator.send_command(bytes.fromhex("AAF10000000000000000FF73"))
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str):
        if not self.coordinator._fan_on:
         return
        self.coordinator._preset_mode = preset_mode
        self.coordinator.update_state()

        if preset_mode == DEVICE_FAN_MODE_LOW:
            command = bytes.fromhex("AAF40100000000000000FF73")
        elif preset_mode == DEVICE_FAN_MODE_MEDIUM:
            command = bytes.fromhex("AAF40200000000000000FF73")
        elif preset_mode == DEVICE_FAN_MODE_HIGH:
            command = bytes.fromhex("AAF40300000000000000FF73")
        else:
            return  #Invalid mode

        await self.coordinator.send_command(command)
        self.async_write_ha_state()