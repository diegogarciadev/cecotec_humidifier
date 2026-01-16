import logging
from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from .coordinator import BLECoordinator
from .const import DOMAIN, WRITE_UUID, NOTIFY_UUID

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    #Create coordinator with device address and mumidifier UUID's
    coordinator = BLECoordinator(
        hass,
        address=entry.data["address"],
        name=entry.data["name"],
        uuid_notify=NOTIFY_UUID,
        uuid_write=WRITE_UUID
    )

    #Initiate integration
    hass.data.setdefault(DOMAIN, {})

    #Store device info
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    _LOGGER.debug("Cecotec Humidifier entry data: %s", entry.data)

    #Try BLE connection
    try:
      await coordinator.connect()
    except Exception as err:
      _LOGGER.error("Can't connect to BLE humidifier: %s", err)
      raise ConfigEntryNotReady from err

    #Load entities
    await hass.config_entries.async_forward_entry_setups(
       entry, 
       ["switch", "binary_sensor", "fan", "select", "light"]
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    if not entry_data:
        return True

    coordinator = entry_data.get("coordinator")

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        ["switch", "binary_sensor", "fan", "select", "light"],
    )

    if coordinator:
        await coordinator.async_shutdown()

    hass.data[DOMAIN].pop(entry.entry_id, None)

    _LOGGER.debug("Cecotec Humidifier entry unloaded: %s", entry.entry_id)

    return unload_ok
