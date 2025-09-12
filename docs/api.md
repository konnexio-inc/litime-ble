---
title: "API"
layout: single
permalink: /api/
---

## BatteryClient

- connect(), disconnect()
- read_once() — synchronous convenience wrapper
- read_once_async() — coroutine performing the exchange
- stream(interval_s) — async generator yielding repeated reads
- session() — async context manager (connect/disconnect)
- sync() — synchronous context manager intended for scripts/CLI

## BatteryStatus

Dataclass with fields:

- voltage_v: float
- current_a: float
- power_w: float
- remaining_ah: float
- capacity_ah: float
- soc_percent: float
- cell_volts_v: list[float]
- cell_temp_c: float
- bms_temp_c: float
- charge_state: enum (idle/charging/discharging)

Methods:

- to_dict()
- json()

## Exceptions

- BatteryError (base)
- BatteryConnectionError
- ProtocolError
- BatteryTimeoutError
