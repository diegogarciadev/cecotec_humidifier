import logging
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, DEVICE_MAX_HOURS, DEVICE_DEFAULT_TIMER_OFF

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        CecotecHumidifierTimerSelect(coordinator)
    ])

class CecotecHumidifierTimerSelect(CoordinatorEntity, SelectEntity):
    """Youngdo/Cecotec humidifier timer control"""
    
    _attr_translation_key = "humidifier_timer"
    _attr_has_entity_name = True
    
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        name = self.coordinator.name
        max_hours = DEVICE_MAX_HOURS.get(name, 12)

        self._attr_unique_id = f"{coordinator.address}_timer"
        self._attr_options = [DEVICE_DEFAULT_TIMER_OFF] + [
            f"{i}h" for i in range(1, max_hours + 1)
        ]

        self._attr_current_option = DEVICE_DEFAULT_TIMER_OFF

    @property
    def native_value(self) -> str:
        if self.coordinator.timer_hours is None:
            return DEVICE_DEFAULT_TIMER_OFF
        return f"{self.coordinator.timer_hours}h"

    @property
    def available(self) -> bool:
        return self.coordinator.is_available and self.coordinator.is_connected #and self.coordinator._fan_on

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info

    async def async_select_option(self, option: str) -> None:
        #If self.coordinator._fan_on in availave property, this if is ignored as is always false
        if not self.coordinator._fan_on:
            _LOGGER.debug("Fan powered off, timer without effect")
            return
        if option == "off":
            self.coordinator._timer_hours = None
            self.coordinator.update_state()
            command = f"AAF20000000000000000FF73"
            await self.coordinator.send_command(bytes.fromhex(command))
            return
        else:
            hours = int(option.rstrip("h"))
            _LOGGER.debug("Timer %s hours", hours)
            self.coordinator._timer_hours = hours
            self.coordinator.update_state()
            command = f"AAF2{hours:02X}00000000000000FF73"
            await self.coordinator.send_command(bytes.fromhex(command))