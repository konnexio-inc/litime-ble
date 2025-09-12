# Battery Core – Reference Code

`battery_core.js` extracted from [litime-bluetooth-battery](https://github.com/chadj/litime-bluetooth-battery/blob/main/index.html).

---

## About the Original Project

The original **Li Time Bluetooth Battery Data Read** is a browser-based app for monitoring the **Li Time 100Ah Group 24 LiFePO4 battery** using the Web Bluetooth API.

- Runs fully client-side in JavaScript, no server required.
- Demonstrates the protocol for reading key states: **temperature, voltage, current, cell voltages, and charge level**.
- Intended as a learning/demonstration tool and freely adaptable.

### Notes

- Tested only with the Li Time 100Ah Group 24 battery (the developer’s hardware).
- Built mainly to experiment with reading battery temperature.
- Live demo: [https://chadj.github.io/litime-bluetooth-battery/](https://chadj.github.io/litime-bluetooth-battery/)

### Browser Support

- Works in Chrome (desktop and Android).
- On iOS, use a Web Bluetooth browser like [WebBLE](https://apps.apple.com/us/app/webble/id1193531073) or [Bluefy](https://apps.apple.com/us/app/bluefy-web-ble-browser/id1492822055).

Mapping to this Python library

The `battery_core.js` reference contains the same connect/request/parse logic used by this Python library. The important mappings are:

- Web Bluetooth service UUID 0xFFE0 -> `SERVICE_UUID` in `client.py` (u16 expansion)
- RX write: 0xFFE2 -> `CHAR_RX_WRITE`
- TX notify: 0xFFE1 -> `CHAR_TX_NOTIFY`
- The 8-byte request packet and parsing offsets are the same; see `client.parse_payload` for the Python implementation.

Use the JavaScript reference to verify offsets and to test in-browser before connecting from Python/Bleak.
