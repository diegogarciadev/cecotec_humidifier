import logging
import math
from datetime import datetime, timedelta
from bleak_retry_connector import (
    establish_connection,
    BleakClientWithServiceCache,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.bluetooth import (
    async_ble_device_from_address,
    BluetoothChange,
    async_register_callback,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import (
    DOMAIN, 
    DEVICE_MAX_BRIGHT, 
    DEVICE_LIGHT_COLORS, 
    DEVICE_DEFAULT_FAN_MODE,
    YOUNGDO_MANUFACTURER,
    AROMA_MANUFACTURER,
    CECOTEC_MANUFACTURER,
    GENERIC_MANUFACTURER,
    DEVICE_FAN_MODE_LOW,
    DEVICE_FAN_MODE_MEDIUM,
    DEVICE_FAN_MODE_HIGH,
    DEVICE_LIGHT_EFFECT_CHANGING
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

class BLECoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, address, name, uuid_notify, uuid_write):
        super().__init__(
            hass,
            _LOGGER,
            name="Cecotec Humidifier BLE",
            update_interval=None,
        )
        self.hass = hass
        self.address = address
        self.name = name
        self.uuid_notify = uuid_notify
        self.uuid_write = uuid_write
        self.client = None
        self.manufacturer = None
        self.model = None
        self.max_bright = DEVICE_MAX_BRIGHT.get(self.name, 255)
        self.data = {
           "fan_on": False,
           "preset_mode": DEVICE_DEFAULT_FAN_MODE,
           "continuous": True,
           "timer_hours": None,
           "remaining_timer_minutes": 0,
           "light_on": False,
           "rgb_color": (255, 255, 255),
           "brightness": self.max_bright,
           "effect": None,
        }
        self._timer_hours = None
        self._remaining_timer_minutes = 0
        self._fan_on = False
        self._preset_mode = DEVICE_DEFAULT_FAN_MODE
        self._continuous = True
        self._light_on = False
        self._rgb_color = (255, 255, 255)
        self._brightness = self.max_bright
        self._effect = None
        self._connected = False
        self._available = False
        self._polling_unsub = None
        self._unsub_bluetooth = None
        self._device_info = self._detect_device_info()

        self._unsub_bluetooth = async_register_callback(
            hass,
            self._async_ble_changed,
            {"address": self.address},
            BluetoothChange.ADVERTISEMENT,
        )             

        _LOGGER.debug("BLE connection UUID's: %s - %s", uuid_notify, uuid_write)

    @property
    def device_info(self) -> DeviceInfo:
      return self._device_info
    
    @property
    def is_connected(self):
        return self._connected
    
    @property
    def is_available(self):
        return self._available
    
    def update_state(self):
      self.data = {
        "fan_on": self._fan_on,
        "preset_mode": getattr(self, "_preset_mode", DEVICE_DEFAULT_FAN_MODE),
        "continuous": self._continuous,
        "timer_hours": self._timer_hours,
        "remaining_timer_minutes": self._remaining_timer_minutes,
        "light_on": self._light_on,
        "rgb_color": self._rgb_color,
        "brightness": self._brightness,
        "effect": self._effect,
      }
      self.async_set_updated_data(self.data)
    
    def _detect_device_info(self) -> DeviceInfo:
      if YOUNGDO_MANUFACTURER.upper() in self.name.upper():
        self.manufacturer = YOUNGDO_MANUFACTURER
      elif AROMA_MANUFACTURER.upper() == self.name.upper():
        self.manufacturer = CECOTEC_MANUFACTURER
      else:
        self.manufacturer = GENERIC_MANUFACTURER

      return DeviceInfo(
        identifiers={(DOMAIN, self.address)},
        connections={("bluetooth", self.address)},
        manufacturer=self.manufacturer,
        model=self.name,
        name=self.name
    )

    async def connect(self):
        device = async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )

        if not device or device is None:
          _LOGGER.debug("No BLE device found with address %s", self.address)
          return
        
        def _create_client(*args, **kwargs):
          return BleakClientWithServiceCache(device, **kwargs)

        _LOGGER.debug(
           "BLEDevice address=%s name=%s metadata=%s details=%s", 
           device.address, 
           getattr(device, "name", None), 
           getattr(device, "metadata", None), 
           getattr(device, "details", None)
        )
        _LOGGER.info("Connecting via HA Bluetooth...")

        try:
            self.client = await establish_connection(
              _create_client,
              device,
              name= device.name,
              timeout=20,
            )
            _LOGGER.info("Client data: %s", self.client)
        except Exception as err:
            _LOGGER.error("Failed to connect to %s", device.name)
            self._connected = False

        if self.client is None:
          _LOGGER.warning("BLE humidifier not connected")
          self._connected = False
          return
        else:
          _LOGGER.info("Client: %s", self.client) 
          if self.client.is_connected:
            _LOGGER.info("Connected to BLE huidifier")
            self._available = True
            self._connected = True
            await self.client.start_notify(self.uuid_notify, self._notification_handler)
            now = datetime.now()
            fecha = now.strftime("%Y-%m-%d %H:%M:%S")
            _LOGGER.debug("Date to send to device: %s", fecha)
            year = int(now.strftime("%Y"))
            month = int(now.strftime("%m"))
            day = int(now.strftime("%d"))
            hours = int(now.strftime("%H"))
            mins = int(now.strftime("%M"))
            secs = int(now.strftime("%S"))
            command = bytes.fromhex(f"AAE1{year:04X}{month:02X}{day:02X}{hours:02X}{mins:02X}{secs:02X}00FF73")
            await self.send_command(command)

            #Query humidifier state
            command = bytes.fromhex("AAF50000000000000000FF73")
            await self.send_command(command)

            #Query light state
            command = bytes.fromhex("AAF90000000000000000FF73")
            await self.send_command(command)

        self._start_polling()    

    def _start_polling(self):
        _LOGGER.debug("Starting polling")
        if self._polling_unsub is None:
            self._polling_unsub = async_track_time_interval(
                self.hass, self._async_check_availability, SCAN_INTERVAL
            )

    def _stop_polling(self):
        _LOGGER.debug("Stopping polling")
        if self._polling_unsub:
            self._polling_unsub()  # esto cancela el track
            self._polling_unsub = None

    def _notification_handler(self, sender, data: bytearray):
        command = data.hex().upper()
        _LOGGER.debug("Notification received: %s", command)
        if command[0:4] == "BBF5":
          _LOGGER.debug("Fog message")
          #ON-OFF
          _LOGGER.debug("ON-OFF: %s", command[4:6])
          if command[4:6] == "01":
             self._fan_on = True
          elif command[4:6] == "00":
             self._fan_on = False
          #TIME
          _LOGGER.debug("TIME: %s", command[6:10])
          self._remaining_timer_minutes = int(command[6:10], 16)
          hours_left = self._remaining_timer_minutes // 60
          _LOGGER.debug("REMAINING MIN: %s", self._remaining_timer_minutes)
          if self._remaining_timer_minutes == 0:
              self._timer_hours = None
          else:
              self._timer_hours = math.ceil(self._remaining_timer_minutes / 60)
          _LOGGER.debug("HOURS LEFT: %s", self._timer_hours)
          #FOG WORK MODE
          _LOGGER.debug("FOG WORK MODE: %s", command[10:12])
          if command[10:12] == "01":
             self._continuous = True
          elif command[10:12] == "02":
             self._continuous = False
          #FOG MODEL
          _LOGGER.debug("FOG MODEL: %s", command[12:14])
          if command[12:14] == "01":
             self._preset_mode = DEVICE_FAN_MODE_LOW
          elif command[12:14] == "02":
             self._preset_mode = DEVICE_FAN_MODE_MEDIUM
          elif command[12:14] == "03":
             self._preset_mode = DEVICE_FAN_MODE_HIGH
        elif command[0:4] == "BBF9":
          #_LOGGER.debug("Light message")
          #ON-OFF
          #_LOGGER.debug("ON-OFF: %s", command[4:6])
          if command[4:6] == "01":
             self._light_on = True
          elif command[4:6] == "00":
             self._light_on = False
          #RGB
          #_LOGGER.debug("RGB: %s", command[6:12])
          self._rgb_color = (int(command[6:8], 16), int(command[8:10], 16), int(command[10:12], 16))
          #LIGHT MODE
          #_LOGGER.debug("LIGHT MODE: %s", int(command[12:14], 16))
          light_mode = int(command[12:14], 16)
          #BRIGHTNESS
          #_LOGGER.debug("BRIGHTNESS: %s", int(command[14:16], 16))
          self._brightness = int(command[14:16], 16)
          #LIGHT SEQUENCE
          #_LOGGER.debug("LIGHT SEQUENCE: %s", int(command[16:18], 16))
          #_LOGGER.debug("LIGHT EFFECT: %s", DEVICE_LIGHT_COLORS[command[16:18]])
          self._effect = DEVICE_LIGHT_COLORS[command[16:18]]
          if light_mode == 1:
             #_LOGGER.debug("Color cambiante")
             self._rgb_color = (255, 255, 255)
             self._effect = DEVICE_LIGHT_EFFECT_CHANGING
          else:
             if int(command[16:18], 16) > 6:
                self._effect = None
        else:
          _LOGGER.debug("Data: %s", command[0:4])
        self.update_state()

    async def send_command(self, command: bytes):
        if self.client and self.client.is_connected:
            await self.client.write_gatt_char(self.uuid_write, command, response=False)
            _LOGGER.debug("Command sent: %s", command.hex())

    @callback
    def _async_check_availability(self, now):
        device = async_ble_device_from_address(self.hass, self.address)
        if device:
          _LOGGER.debug("Device exist")
          if not self._available:
            _LOGGER.info("Humidifier %s detected again", self.address)
          self._available = True
        else:
          _LOGGER.debug("Device not exist")
          if self._available:
            _LOGGER.warning("Humidifier %s out of BT range", self.address)
          self._available = False
          self._connected = False
          self.client = None 
          self._stop_polling()

        if self.client is None or not self.client.is_connected:
            _LOGGER.debug("Humidifier %s disconnected, trying to reconnect...", self.address)
            self._connected = False
            self.hass.create_task(self._async_reconnect())
        else:
            _LOGGER.debug("Humidifier %s still connected", self.address)
            self._connected = True

        _LOGGER.debug("States: available - connected: %s - %s", self._available, self._connected)
        self.async_set_updated_data(self.data)

    @callback
    def _async_ble_changed(self, device, change):
      _LOGGER.debug("BLE device: %s", device);
      _LOGGER.debug("BLE change: %s", change);
      if change == BluetoothChange.ADVERTISEMENT:
        _LOGGER.debug("BLE humidifier detected: %s", device.address)
        self._available = True
        self._start_polling()

      if self.client and not self.client.is_connected:
        _LOGGER.warning("BLE humidifier disconnected")
        self.device = device
        self.hass.create_task(self._async_reconnect())

      self.async_set_updated_data(None)

    async def _async_reconnect(self):
      if self._connected:
        _LOGGER.debug("Already connected, canceling reconnection...")
        return

      try:
        await self.connect()
      except Exception as err:
        _LOGGER.warning("Can't connect to humidifier %s: %s", self.address, err)
        self._connected = False
      _LOGGER.info("Successfully reconnected to humidifier %s", self.address)
      self.async_set_updated_data(self.data)

    async def async_shutdown(self):
      if self._unsub_bluetooth:
        self._unsub_bluetooth()
        self._unsub_bluetooth = None

      if self.client:
        await self.client.disconnect()
        self.client = None
