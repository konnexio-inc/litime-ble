from __future__ import annotations
import argparse
from .client import BatteryClient
from .discovery import discover_devices_sync, format_device_info
from .logging import get_logger

logger = get_logger()


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="litime-battery", description="Read Li Time BLE battery"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    # Read command
    rd = sub.add_parser("read", help="Read once")
    rd.add_argument("--address", help="BLE MAC")
    rd.add_argument("--name", help="BLE device name")
    rd.add_argument("--json", action="store_true", help="Output JSON")
    rd.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Discover command
    disc = sub.add_parser("discover", help="Discover BLE devices")
    disc.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Scan timeout in seconds (default: 10)",
    )
    disc.add_argument(
        "--battery-only", action="store_true", help="Show only Li-Time battery devices"
    )
    disc.add_argument("--services", action="store_true", help="Show service UUIDs")
    disc.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = ap.parse_args()

    # Enable debug logging if requested
    if hasattr(args, "debug") and args.debug:
        from .logging import configure_logging, DEBUG

        configure_logging(DEBUG)
        logger.debug("Debug logging enabled via CLI")

    if args.cmd == "read":
        client = BatteryClient(address=args.address, name=args.name)
        try:
            s = client.read_once()
            logger.debug("Battery read completed successfully")
        except Exception as e:
            logger.error("Battery read failed: %s: %s", type(e).__name__, e)
            raise

        if args.json:
            print(s.json())
        else:
            print(f"Voltage:      {s.voltage_v:.3f} V")
            print(f"Current:      {s.current_a:.3f} A")
            print(f"Power:        {s.power_w:.2f} W")
            print(f"RemainingAh:  {s.remaining_ah:.2f} Ah")
            print(f"CapacityAh:   {s.capacity_ah:.2f} Ah")
            print(f"SoC:          {s.soc_percent:.2f} %")
            print(f"Cell volts:   {', '.join(f'{v:.3f}' for v in s.cell_volts_v)}")
            print(f"Cell temp:    {s.cell_temp_c:.1f} °C")
            print(f"BMS temp:     {s.bms_temp_c:.1f} °C")
            print(f"State:        {s.charge_state.value}")

    elif args.cmd == "discover":
        try:
            print(f"Scanning for BLE devices (timeout: {args.timeout}s)...")
            devices = discover_devices_sync(
                timeout=args.timeout, include_battery_only=args.battery_only
            )

            if not devices:
                print("No devices found.")
                return

            print(f"\nFound {len(devices)} device(s):")
            print("-" * 60)

            for device in devices:
                print(format_device_info(device, show_services=args.services))
                if args.services:
                    print()  # Extra spacing when showing services

            # Summary
            battery_count = sum(1 for d in devices if d["is_litime_battery"])
            if battery_count > 0:
                print(f"\n✓ Found {battery_count} Li-Time battery device(s)")
            else:
                print("\nNo Li-Time battery devices found.")

        except Exception as e:
            logger.error("Device discovery failed: %s: %s", type(e).__name__, e)
            print(f"Error: {e}")
            raise
