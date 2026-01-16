import logging
from homeassistant.components.light import (
    LightEntity,
    LightEntityFeature,
    ColorMode,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import BLECoordinator
from .const import DOMAIN, DEVICE_LIGHT_EFFECT_LIST, BLE_NAME_PATTERN_YOUNGDO_AROMA

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: BLECoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        CecotecHumidifierLight(coordinator)
    ])

class CecotecHumidifierLight(CoordinatorEntity, LightEntity):
    """Youngdo/Cecotec humidifier light control"""

    _attr_translation_key = "humidifier_light"
    _attr_has_entity_name = True
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_supported_color_modes = {ColorMode.RGB, ColorMode.HS, ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.RGB

    def __init__(self, coordinator: BLECoordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_light"

    @property
    def is_on(self) -> bool:
        return self.coordinator._light_on

    @property
    def brightness(self) -> int:
        return self.coordinator._brightness

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        return self.coordinator._rgb_color

    @property
    def effect(self) -> str | None:
        return self.coordinator._effect

    @property
    def effect_list(self) -> list[str]:
        return DEVICE_LIGHT_EFFECT_LIST

    @property
    def available(self) -> bool:
        return self.coordinator.is_available and self.coordinator.is_connected

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info
    
    async def async_turn_on(self, **kwargs):   
        _LOGGER.debug("Light arguments: %s", kwargs)

        # Update kwargs values into coordinator
        if "rgb_color" in kwargs:
            self.coordinator._rgb_color = kwargs["rgb_color"]
        if "brightness" in kwargs:
            self.coordinator._brightness = kwargs["brightness"]
        if "effect" in kwargs:
            self.coordinator._effect = kwargs["effect"]

        if not self.coordinator._light_on:
            command = bytes.fromhex("AAF60100000000000000FF73")
            await self.coordinator.send_command(command)
            #Start with max bright
            #self.coordinator._rgb_color = (255, 255, 255)
            #Start with white color
            #command = bytes.fromhex("AAFC0600000000000000FF73")
            #await self.coordinator.send_command(command)
            self.coordinator._light_on = True

        if "effect" in kwargs:
          if self.coordinator._effect == "red":
              self.coordinator._rgb_color = (255, 0, 0)
              command = bytes.fromhex("AAFC0000000000000000FF73")
          elif self.coordinator._effect == "pink":
              self.coordinator._rgb_color = (255, 0, 255)
              command = bytes.fromhex("AAFC0100000000000000FF73")
          elif self.coordinator._effect == "blue":
              self.coordinator._rgb_color = (0, 0, 255)
              command = bytes.fromhex("AAFC0200000000000000FF73")
          elif self.coordinator._effect == "cyan":
              self.coordinator._rgb_color = (0, 255, 255)
              command = bytes.fromhex("AAFC0300000000000000FF73")
          elif self.coordinator._effect == "green":
              self.coordinator._rgb_color = (0, 255, 0)
              command = bytes.fromhex("AAFC0400000000000000FF73")
          elif self.coordinator._effect == "yellow":
              self.coordinator._rgb_color = (255, 255, 0)
              command = bytes.fromhex("AAFC0500000000000000FF73")
          elif self.coordinator._effect == "white":
              self.coordinator._rgb_color = (255, 255, 255)
              command = bytes.fromhex("AAFC0600000000000000FF73")
          elif self.coordinator._effect == "changing":
              if self.coordinator.name == BLE_NAME_PATTERN_YOUNGDO_AROMA:
                  command = bytes.fromhex("AAFC0700000000000000FF73")
              else:
                  command = bytes.fromhex("AAFA0000000000000000FF73")   
          elif self.coordinator._effect == "rhythm":
              command = bytes.fromhex("AAF80100000000000000FF73")
          await self.coordinator.send_command(command)

        if "brightness" in kwargs:
            command = bytes.fromhex(command)   
            await self.coordinator.send_command(command)      
        
        if "rgb_color" in kwargs:
            self.coordinator._effect = None
            r, g, b = self.coordinator._rgb_color
            command = bytes([0xAA, 0xF7, r, g, b, 0, 0, 0, 0, 0, 0xFF, 0x73])
            await self.coordinator.send_command(command)

        self.coordinator.update_state()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self.coordinator._light_on = False
        self.coordinator._effect = None
        command = bytes.fromhex("AAF60000000000000000FF73")
        await self.coordinator.send_command(command)
        self.async_write_ha_state()
