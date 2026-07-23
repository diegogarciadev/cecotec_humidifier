import logging
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.helpers import config_validation as cv
from .const import (
    DOMAIN,
    BLE_NAME_PATTERN_AROMA,
    BLE_NAME_PATTERN_YOUNGDO_BLE,
    BLE_NAME_PATTERN_YOUNGDO_AROMA,
    YOUNGDO_MANUFACTURER,
    AROMA_MANUFACTURER,
    CECOTEC_MANUFACTURER,
    GENERIC_MANUFACTURER
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak):
        _LOGGER.debug("ConfigFlow launched")
        if discovery_info is None:
            _LOGGER.debug("discovery_info is None")
            return self.async_create_entry(
                title=self.context["title"],
                data=self.context["data"],
            )
        
        _LOGGER.debug("discovery_info is not None")
        
        self.name = discovery_info.name or ""
        self.address = discovery_info.address

        _LOGGER.debug("async_step_bluetooth: name=%s address=%s", self.name, self.address)

        if (
        (BLE_NAME_PATTERN_AROMA not in (self.name or "")) and 
        (BLE_NAME_PATTERN_YOUNGDO_BLE not in (self.name or "")) and 
        (BLE_NAME_PATTERN_YOUNGDO_AROMA not in (self.name or ""))
        ):
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(self.address)
        self._abort_if_unique_id_configured()

        if YOUNGDO_MANUFACTURER in self.name:
          self.manufacturer = YOUNGDO_MANUFACTURER
        elif AROMA_MANUFACTURER == self.name:
          self.manufacturer = CECOTEC_MANUFACTURER
        else:
          self.manufacturer = GENERIC_MANUFACTURER

        #return self.async_create_entry(
        #    title=self.manufacturer,
        #    data={
        #        "address": discovery_info.address,
        #        "name": discovery_info.name,
        #    },
        #)

        self.device_name = f"{self.name} ({self.address})"

        self.context["title"] = self.manufacturer
        self.context["data"] = {
            "address": self.address,
            "name": self.name,
        }

        #self._set_confirm_only()
        #return self.async_show_form(
        #    step_id="bluetooth",
        #    description_placeholders={
        #        "name": self.device_name
        #    },
        #)

        return await self.async_step_discovery_confirm()

        placeholders = {"name": self.device_name}
        self.context["title_placeholders"] = placeholders

        return self.async_show_form(
            step_id="bluetooth",
            description_placeholders=placeholders
        )

    async def async_step_discovery_confirm(self, user_input = None):    
        if user_input is not None:
            _LOGGER.debug("user_input is not None")
            return self.async_create_entry(
                title=self.context["title"],
                data=self.context["data"],
            )
        self._set_confirm_only()
        errors = {
           "general" : "error_general"
        }
        placeholders = {
           "name": self.device_name,
           "address": self.address,
           "manufacturer": self.manufacturer 
        }
        self.context["title_placeholders"] = placeholders
        return self.async_show_form(
            step_id="discovery_confirm", 
            description_placeholders=placeholders,
            errors=errors,
        )

    async def async_step_user(self, user_input=None):
        #Only discovery integration 
        return self.async_abort(reason="bluetooth_only")
    