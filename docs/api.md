---
title: "API"
layout: single
permalink: /api/
---

## BatteryClient

Primary class for battery interaction:

- `connect()`, `disconnect()` - Manual connection management
- `read_once()` - Synchronous convenience wrapper
- `read_once_async()` - Coroutine performing the BLE exchange
- `stream(interval_s)` - Async generator yielding repeated reads
- `session()` - Async context manager (connect/disconnect)
- `sync()` - Synchronous context manager intended for scripts/CLI

## Device Discovery (New in 0.2.0)

Functions for finding Li-Time batteries and BLE devices:

- `discover_devices(timeout=8.0)` - Async: scan for all BLE devices
- `discover_devices_sync(timeout=8.0)` - Sync: scan for all BLE devices
- `find_litime_batteries(timeout=8.0)` - Async: find only Li-Time batteries
- `find_litime_batteries_sync(timeout=8.0)` - Sync: find only Li-Time batteries
- `format_device_info(device, show_services=False)` - Format device info for display

## Logging (New in 0.2.0)

Configurable logging system:

- `configure_logging(level)` - Set logging level
- `DEBUG`, `INFO`, `WARNING`, `ERROR` - Log level constants

## BatteryStatus

Dataclass with battery state fields:

- `voltage_v: float` - Battery voltage in volts
- `current_a: float` - Current in amperes (+ charging, - discharging)
- `power_w: float` - Power in watts
- `remaining_ah: float` - Remaining capacity in amp-hours
- `capacity_ah: float` - Total capacity in amp-hours
- `soc_percent: float` - State of charge percentage
- `cell_volts_v: list[float]` - Individual cell voltages
- `cell_temp_c: float` - Cell temperature in Celsius
- `bms_temp_c: float` - BMS temperature in Celsius
- `charge_state: ChargeState` - Enum (idle/charging/discharging)

Methods:

- `to_dict()` - Convert to dictionary
- `json()` - Serialize to JSON string

## ChargeState

Enum representing battery charging state:

- `ChargeState.IDLE` - Not charging or discharging
- `ChargeState.CHARGING` - Currently charging
- `ChargeState.DISCHARGING` - Currently discharging

## Exceptions

Hierarchy of battery-related exceptions:

- `BatteryError` - Base exception for all battery operations
- `BatteryConnectionError` - Connection/disconnection failures
- `ProtocolError` - BLE protocol or data parsing errors
- `BatteryTimeoutError` - Operation timeout errors
