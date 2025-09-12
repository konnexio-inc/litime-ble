# Examples

Short, focused example scripts for the Li-Time BLE library. They are small CLI tools intended for manual testing or to be used inside CI demos. Most scripts accept `--mac` (when applicable) and `--debug`.

## Quick list

- `battery_read_sync.py` — simple synchronous battery read. Flags: `--mac`, `--debug`.
- `battery_read_async.py` — async reader with retries. Flags: `--mac`, `--debug`.
- `device_discovery.py` — find BLE devices and Li‑Time batteries. Flags: `--timeout`, `--battery-only`, `--sync`, `--non-interactive`, `--debug`.
- `debug_test.py` — quick debug read (used for troubleshooting). Flags: `--mac`, `--debug`.
- `logging_test.py` — demonstrates logging levels and performs a test read. Flags: `--mac`, `--request-timeout`, `--debug`.

## Run (PowerShell)

```powershell
# Sync read (prints formatted + JSON)
python .\examples\battery_read_sync.py --mac C8:47:80:15:5C:0F

# Async read with debug logging
python .\examples\battery_read_async.py --mac C8:47:80:15:5C:0F --debug

# Device discovery (battery-only, non-interactive)
python .\examples\device_discovery.py --battery-only --non-interactive --timeout 5

# Quick debug read with DEBUG logging
python .\examples\debug_test.py --mac C8:47:80:15:5C:0F --debug

# Logging demo
python .\examples\logging_test.py --mac C8:47:80:15:5C:0F --debug
```

## Notes

- Default MAC shown in examples is `C8:47:80:15:5C:0F` — replace it with your battery's MAC.
- `--debug` turns on detailed internal logs which help diagnose connection and parsing issues.
- `device_discovery.py` supports a `--non-interactive` mode suitable for CI or scripts; omitting it will prompt for a choice.

## Troubleshooting checklist

1. Run discovery first to find your battery: `python .\examples\device_discovery.py --battery-only --non-interactive`.
2. Confirm the MAC address reported by discovery and use it for the read examples.
3. Ensure the battery is powered on and within Bluetooth range.
4. Make sure no other device is currently connected to the battery.
5. If things fail, re-run with `--debug` and inspect the logs for details.

You can also run the package CLI when installed (e.g. `python -m litime_ble`) for higher-level commands.

The examples are intentionally small and script-friendly so you can automate them in tests or demos.
