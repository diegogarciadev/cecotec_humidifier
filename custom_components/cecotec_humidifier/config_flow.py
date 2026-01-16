import logging
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from .const import (
    DOMAIN,
    BLE_NAME_PATTERN_AROMA,
    BLE_NAME_PATTERN_YOUNGDO_BLE,
    BLE_NAME_PATTERN_YOUNGDO_AROMA,
    YOUNGDO_MANUFACTURER,
    AROMA_MANUFACTURER,
    CECOTEC_MANUFACTURAR,
    GENERIC_MANUFACTURAR
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak):
        _LOGGER.debug("ConfigFlow launched")
        _LOGGER.debug("async_step_bluetooth: name=%s address=%s", discovery_info.name, discovery_info.address)
        if (
        (BLE_NAME_PATTERN_AROMA not in (discovery_info.name or "")) and 
        (BLE_NAME_PATTERN_YOUNGDO_BLE not in (discovery_info.name or "")) and 
        (BLE_NAME_PATTERN_YOUNGDO_AROMA not in (discovery_info.name or ""))
        ):
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        if YOUNGDO_MANUFACTURER in discovery_info.name:
          self.manufacturer = YOUNGDO_MANUFACTURER
        elif AROMA_MANUFACTURER == discovery_info.name:
          self.manufacturer = CECOTEC_MANUFACTURAR
        else:
          self.manufacturer = GENERIC_MANUFACTURAR

        return self.async_create_entry(
            title=self.manufacturer,
            data={
                "address": discovery_info.address,
                "name": discovery_info.name,
            },
        )

    async def async_step_user(self, user_input=None):
        #Only discovery integration 
        return self.async_abort(reason="bluetooth_only")
