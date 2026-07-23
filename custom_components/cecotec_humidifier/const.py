DOMAIN = "cecotec_humidifier"

BLE_NAME_PATTERN_AROMA = "Aroma"
BLE_NAME_PATTERN_YOUNGDO_BLE = "Youngdo_Ble"
BLE_NAME_PATTERN_YOUNGDO_AROMA = "youngdo-Aroma"

WRITE_UUID = "0000ae01-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000ae02-0000-1000-8000-00805f9b34fb"

DEVICE_DEFAULT_FAN_MODE = "low"
DEVICE_DEFAULT_TIMER_OFF = "off"
DEVICE_FAN_MODE_LOW = "low"
DEVICE_FAN_MODE_MEDIUM = "medium"
DEVICE_FAN_MODE_HIGH = "high"

YOUNGDO_MANUFACTURER = "Youngdo"
AROMA_MANUFACTURER = "Aroma"
CECOTEC_MANUFACTURER = "Cecotec"
GENERIC_MANUFACTURER = "Generic"

DEVICE_MAX_HOURS = {
    "Aroma": 12,
    "Youngdo_Ble": 10,
    "youngdo-Aroma": 9,
}

DEVICE_MAX_BRIGHT = {
    "Aroma": 255,
    "Youngdo_Ble": 100,
    "youngdo-Aroma": 255,
}

DEVICE_FAN_MODES = [
    "low",
    "medium",
    "high"
]

DEVICE_LIGHT_COLORS = {
    "00": "red",
    "01": "pink",
    "02": "blue",
    "03": "cyan",
    "04": "green",
    "05": "yellow",
    "06": "white",
    "07": "gray",
    "08": "orange",
}

DEVICE_LIGHT_EFFECT_LIST = [
    "red",
    "pink",
    "blue",
    "cyan",
    "green",
    "yellow",
    "white",
    "changing",
    "rhythm"
]

DEVICE_LIGHT_EFFECT_CHANGING = "changing"

