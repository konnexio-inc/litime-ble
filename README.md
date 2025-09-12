# litime-ble

Lightweight Python library and CLI to read Li-Time BLE battery statistics via Bluetooth Low Energy.

**New in 0.2.0**: Device discovery, enhanced logging, comprehensive examples, and CLI module support.

## Install

```bash
pip install litime-ble
```

Or install from source:

```bash
pip install .
```

## Quick start

### Device Discovery

Find your Li-Time battery automatically:

```python
from litime_ble import find_litime_batteries_sync

batteries = find_litime_batteries_sync(timeout=5.0)
if batteries:
    mac_address = batteries[0]['address']
    print(f"Found battery: {mac_address}")
```

### Battery Reading

```python
from litime_ble import BatteryClient

# Synchronous (simple)
with BatteryClient.sync(address="C8:47:80:15:5C:0F") as client:
    status = client.read_once()
    print(f"Battery: {status.voltage_v:.1f}V, {status.soc_percent:.0f}%")
    print(status.json())  # Full data as JSON

# Asynchronous (recommended)
import asyncio
from litime_ble import BatteryClient

async def read_battery():
    client = BatteryClient(address="C8:47:80:15:5C:0F")
    async with client.session():
        status = await client.read_once_async()
        return status

status = asyncio.run(read_battery())
```

## CLI

```bash
# Discover batteries
python -m litime_ble discover --battery-only

# Read battery status
python -m litime_ble read --address C8:47:80:15:5C:0F --json

# Or use the installed command
litime-battery read --address C8:47:80:15:5C:0F --json
```

## Documentation & Examples

- **[Documentation](https://konnexio-inc.github.io/litime-ble/)** - Complete API docs and usage guide
- **[Examples](examples/)** - Ready-to-run example scripts with CLI options
- **[Developer Guide](docs/developer.md)** - Setup, testing, and contribution guidelines

## Developer

**Quick test:**

```bash
# PowerShell
$env:PYTHONPATH = (Resolve-Path src).Path; python -m pytest -q

# macOS/Linux
PYTHONPATH=$(pwd)/src python -m pytest -q
```

**Code quality:**

```bash
ruff check src --fix
```

## License

This project is licensed under the [MIT License](./LICENSE).  
It follows the same license as the original codebase it was based on: [litime-bluetooth-battery](https://github.com/chadj/litime-bluetooth-battery).

Copyright (c) 2025 Konnexio Inc.
