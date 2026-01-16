# Cecotec & Youngdo Humidifier – Home Assistant Custom Integration

This custom Home Assistant integration allows you to control compatible **Cecotec** and **Youngdo** humidifiers directly from Home Assistant.

The integration focuses on core humidifier and lighting features exposed by these devices, including humidity control, fan speeds, timers, and advanced lighting modes such as color effects and music-reactive lighting via Bluetooth.

---

## 🔎 Device Discovery & Configuration

This integration performs **automatic device discovery** on the local network and automatically adds supported devices to Home Assistant.

⚠️ **Important:**  
This integration **does not provide a configuration flow (Config Flow)**.

No UI-based setup or configuration screen is available at this time.

---

## ✨ Features

### 💧 Humidifier Control
- Turn the humidifier **on / off**
- Control **3 fan speeds**
- **Timer** support
- Enable or disable **continuous mode**

### 💡 Light Control
- Turn the light **on / off**
- **Fixed color** mode
- **Color changing effect**
- **Music reactive mode** (light reacts to Bluetooth audio rhythm)

---

## 🎵 Music Reactive Lighting

When **rhythm light mode** is enabled, the humidifier light reacts to the rhythm of audio played through the device’s Bluetooth connection.

> ℹ️ Make sure your phone or audio source is connected to the humidifier via Bluetooth.

---

## 🧩 Supported Devices

- Cecotec humidifiers
- Youngdo humidifiers

> ⚠️ **Note:** Device compatibility may vary depending on firmware and model.  
> This integration has been tested only with specific devices (Cecotec PureAroma 550).

---

## 📦 Installation

### Option 1: Manual Installation

1. Download or clone this repository.
2. Copy the integration folder into your Home Assistant `custom_components` directory:

   ```text
   config/
   └── custom_components/
       └── cecotec_humidifier/
           ├── __init__.py
           ├── manifest.json
           ├── light.py
           ├── fan.py
           └── ...
3. Restart Home Assistant.

---

## 🚧 Known Limitations

- Limited number of tested device models
- Bluetooth music mode depends on device firmware

---

## 🛠️ Development Status

This integration is under active development.

### Planned improvements

- Add alarm support
- Expanded device compatibility
- Improved error handling

---

## 📄 Disclaimer

This project is **not affiliated**, **associated**, **authorized**, **endorsed by**, or in any way officially connected with **Cecotec** or **Youngdo**, or any of their subsidiaries or affiliates.

All product names, logos, brands, and trademarks mentioned are the property of their respective owners.