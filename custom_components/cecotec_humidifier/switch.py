from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities(
        [
            CecotecHumidifierContinuousModeSwitch(coordinator),
        ]
    )

class CecotecHumidifierContinuousModeSwitch(CoordinatorEntity, SwitchEntity):
    """Youngdo/Cecotec humidifier continuous mode control"""

    _attr_translation_key = "humidifier_continuousmode_switch"
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_continuous"
        self._attr_icon = "mdi:sync"

    @property
    def is_on(self) -> bool | None:
        return self.coordinator._continuous
    
    @property
    def available(self):
        return self.coordinator.is_available and self.coordinator.is_connected and self.coordinator._fan_on

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info

    async def async_turn_on(self, **kwargs):
        command = bytes.fromhex("AAF30100000000000000FF73")
        await self.coordinator.send_command(command)
        self.coordinator._continuous = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        command = bytes.fromhex("AAF30200000000000000FF73")
        await self.coordinator.send_command(command)
        self.coordinator._continuous = False
        self.async_write_ha_state()