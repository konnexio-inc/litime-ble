---
title: "Usage"
layout: single
permalink: /usage/
---

## Installation

```bash
pip install litime-ble
```

Or install from source:

```bash
pip install .
```

## Device Discovery (New in 0.2.0)

Find your Li-Time battery automatically:

```python
from litime_ble import find_litime_batteries_sync

# Find Li-Time batteries
batteries = find_litime_batteries_sync(timeout=5.0)
if batteries:
    mac_address = batteries[0]['address']
    print(f"Found battery: {mac_address}")

# Or find all BLE devices
from litime_ble import discover_devices_sync
all_devices = discover_devices_sync(timeout=5.0)
```

## Battery Reading

### Synchronous (convenience)

```python
from litime_ble import BatteryClient

with BatteryClient.sync(address="C8:47:80:15:5C:0F") as client:
    status = client.read_once()
    print(f"Battery: {status.voltage_v:.1f}V, {status.soc_percent:.0f}%")
    print(status.json())
```

> Note: `sync()` creates a temporary event loop and is intended for scripts/CLI. In a running asyncio application use the async API.

### Asynchronous (recommended)

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

## Logging (New in 0.2.0)

Enable detailed logging for debugging:

```python
from litime_ble import configure_logging, DEBUG

# Enable debug logging
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

## Examples

See the `examples/` directory for comprehensive example scripts:

- `device_discovery.py` - Interactive and automated device discovery
- `battery_read_sync.py` - Simple synchronous battery reading
- `battery_read_async.py` - Async reading with retries
- `debug_test.py` - Quick debugging tool
- `logging_test.py` - Logging demonstration
