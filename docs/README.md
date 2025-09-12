# litime-ble — documentation

This document contains protocol details, usage examples, API notes, and developer instructions.

**New in 0.2.0**: Device discovery, enhanced logging, comprehensive examples, and CLI module support.

## Installation

```bash
pip install litime-ble
```

Or install from source:

```bash
pip install .
```

## Quick Start

### Device Discovery (New in 0.2.0)

Find your Li-Time battery automatically:

```python
from litime_ble import find_litime_batteries_sync

batteries = find_litime_batteries_sync(timeout=5.0)
if batteries:
    mac_address = batteries[0]['address']
    print(f"Found battery: {mac_address}")
```

### Battery Reading

#### Synchronous (convenience)

```python
from litime_ble import BatteryClient

with BatteryClient.sync(address="C8:47:80:15:5C:0F") as client:
    status = client.read_once()
    print(f"Battery: {status.voltage_v:.1f}V, {status.soc_percent:.0f}%")
    print(status.json())
```

> Note: `sync()` creates a temporary event loop and is intended for scripts/CLI. In a running asyncio application use the async API.

#### Asynchronous (recommended)

```python
import asyncio
from litime_ble import BatteryClient

async def main():
    client = BatteryClient(address="C8:47:80:15:5C:0F")
    async with client.session():
        status = await client.read_once_async()
        print(status.json())

asyncio.run(main())
```

### Logging (New in 0.2.0)

Enable debug logging for troubleshooting:

```python
from litime_ble import configure_logging, DEBUG

configure_logging(DEBUG)
# Your battery operations will now show detailed logs
```

## CLI

### Module CLI (New in 0.2.0)

```bash
# Discover batteries
python -m litime_ble discover --battery-only

# Read battery status
python -m litime_ble read --address C8:47:80:15:5C:0F --json
```

### Installed CLI

```bash
# Read battery
litime-battery read --address C8:47:80:15:5C:0F --json

# Discover devices
litime-battery discover --battery-only
```

## API summary

- BatteryClient
  - connect(), disconnect()
  - read_once() — synchronous convenience wrapper
  - read_once_async() — coroutine that performs write/notify exchange
  - stream(interval_s) — async generator
  - session() — async context manager
  - sync() — sync context manager (scripts only)
- BatteryStatus dataclass — parsed numeric fields and helpers
- Exceptions (in `litime_ble.errors`)
  - BatteryError (base)
  - BatteryConnectionError
  - ProtocolError
  - BatteryTimeoutError

## Protocol / packet

- Service UUID: 0xFFE0
- TX notify (battery -> client): 0xFFE1
- RX write (client -> battery): 0xFFE2
- Request command (8 bytes): `00 00 01 04 55 13 17 AA`

### Parse mapping (notification payload offsets)

- Voltage: uint32le at offset 12 -> divide by 1000 -> V
- Current: int32le at offset 48 -> divide by 1000 -> A
- Remaining Ah: uint16le at offset 62 -> divide by 100 -> Ah
- Capacity Ah: uint16le at offset 64 -> divide by 100 -> Ah
- Cell voltages: 16 × uint16le starting at 16 -> divide by 1000 -> V (ignore zeros)
- Cell temp: int16le at offset 52 -> °C
- BMS temp: int16le at offset 54 -> °C

## Developer

Run tests

PowerShell

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
python -m pytest -q
```

macOS / Linux

```bash
PYTHONPATH=$(pwd)/src python -m pytest -q
```

Windows (cmd.exe)

```cmd
set PYTHONPATH=%cd%\src && python -m pytest -q
```

Linting

```bash
ruff check src --fix
ruff check src
```

## Notes

- The `sync()` helper is provided for convenience in scripts and CLIs; prefer the async API in running event loops.
- If your pack uses different offsets or packet formats, adjust `parse_payload()` accordingly or provide an adapter.
