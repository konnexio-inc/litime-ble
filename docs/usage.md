---
title: "Usage"
layout: single
permalink: /usage/
---

Install from the repository root:

```bash
pip install .
```

## Synchronous (convenience)

```python
from litime_ble import BatteryClient

with BatteryClient.sync(address="AA:BB:CC:DD:EE:FF") as client:
    status = client.read_once()
    print(status.json())
```

> Note: `sync()` creates a temporary event loop and is intended for scripts/CLI. In a running asyncio application use the async API.

## Asynchronous

```python
import asyncio
from litime_ble import BatteryClient

async def main():
    client = BatteryClient(address="AA:BB:CC:DD:EE:FF")
    async with client.session():
        status = await client.read_once_async()
        print(status.json())

asyncio.run(main())
```

## CLI

```bash
litime-battery read --address AA:BB:CC:DD:EE:FF --json
```
