# litime-ble

Lightweight Python library and CLI to read Li Time BLE battery statistics.

## Install

Install from source:

```bash
pip install .
```

## Quick start

Example (synchronous helper):

```python
from litime_ble import BatteryClient

with BatteryClient.sync(address="AA:BB:CC:DD:EE:FF") as client:
    status = client.read_once()
    print(status.json())
```

## CLI

```bash
litime-battery read --address AA:BB:CC:DD:EE:FF --json
```

For protocol details and advanced usage see `docs/README.md`.

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

## License

This project is licensed under the [MIT License](./LICENSE).  
It follows the same license as the original codebase it was based on: [litime-bluetooth-battery](https://github.com/chadj/litime-bluetooth-battery).

Copyright (c) 2024 Chad Johnson  
Copyright (c) 2025 Konnexio Inc.
