/**
 * File: battery_core.js
 *
 * Contains only the **battery communication + parsing logic**
 * extracted from the Li Time Bluetooth web demo.
 *
 * Removed: UI, HTML, CSS, DOM updates, footer/alerts.
 * Kept: Web Bluetooth connect (0xFFE0), request packet (8 bytes),
 *       notification parsing (voltage, current, capacity, remainingAh,
 *       cell voltages, temps), 3s polling loop.
 *
 * Purpose: Minimal functional reference for connect, request, decode.
 *
 * Usage: Call `connectBattery()` in Chrome with Web Bluetooth.
 *        Parsed stats log to console.
 *
 * Ref: https://github.com/chadj/litime-bluetooth-battery
 */

function timeout(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const fmt = new Intl.NumberFormat("en-US", { maximumSignificantDigits: 4 });

function parseNotification(event) {
  const packet = event.target.value;
  const payload = new DataView(packet.buffer);

  let voltage = payload.getUint32(12, true) / 1000;
  let current = payload.getInt32(48, true) / 1000;
  let remainingAh = payload.getUint16(62, true) / 100;
  let capacityAh = payload.getUint16(64, true) / 100;

  let cellVolts = [];
  let offset = 16;
  for (let x = 0; x < 16; x++) {
    let cellVolt = payload.getUint16(offset + x * 2, true);
    if (cellVolt !== 0) {
      cellVolts.push(cellVolt / 1000);
    }
  }

  let cellTempC = payload.getInt16(52, true);
  let bmsTempC = payload.getInt16(54, true);

  return {
    voltage,
    current,
    remainingAh,
    capacityAh,
    cellVolts,
    cellTempC,
    bmsTempC,
  };
}

async function connectBattery() {
  let device = await navigator.bluetooth.requestDevice({
    filters: [{ services: [0xffe0] }],
  });
  let server = await device.gatt.connect();
  let service = await server.getPrimaryService(0xffe0);
  let rxCharacteristic = await service.getCharacteristic(0xffe2);
  let txCharacteristic = await service.getCharacteristic(0xffe1);
  await txCharacteristic.startNotifications();

  txCharacteristic.addEventListener("characteristicvaluechanged", (event) => {
    try {
      const stats = parseNotification(event);
      console.log(stats);
    } catch (error) {
      console.error(error);
    }
  });

  let requestType = "";

  async function requestReady() {
    while (true) {
      if (requestType === "") {
        break;
      }
      await timeout(250);
    }
  }

  async function getStats() {
    const buffer = new ArrayBuffer(8);
    const view = new DataView(buffer);
    view.setUint16(0, 0x0000);
    view.setUint16(2, 0x0401);
    view.setUint16(4, 0x1355);
    view.setUint16(6, 0xaa17);

    requestType = "getStats";
    if (rxCharacteristic.writeValueWithResponse) {
      await rxCharacteristic.writeValueWithResponse(buffer);
    } else {
      await rxCharacteristic.writeValue(buffer);
    }
  }

  while (true) {
    try {
      await getStats();
      await requestReady();
    } catch (err) {
      console.error(err);
    }
    await timeout(3000);
  }
}
