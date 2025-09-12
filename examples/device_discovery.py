"""
Device discovery example for Li-Time BLE library.

This example demonstrates:
- Scanning for all BLE devices
- Filtering for Li-Time battery devices only
- Displaying device information including MAC addresses and service UUIDs

Usage:
    python examples/device_discovery.py [--timeout N] [--battery-only] [--sync] [--non-interactive] [--debug]
"""

import argparse
import asyncio
from typing import Optional

from litime_ble import (
    discover_devices,
    find_litime_batteries,
    format_device_info,
    configure_logging,
    INFO,
    DEBUG,
)


async def main_async(timeout: float, battery_only: bool, debug: bool) -> None:
    """Async discovery demonstration."""
    configure_logging(DEBUG if debug else INFO)

    if battery_only:
        print("Scanning for Li-Time battery devices only...")
        battery_devices = await find_litime_batteries(timeout=timeout)

        if battery_devices:
            print(f"\nFound {len(battery_devices)} Li-Time battery device(s):")
            print("-" * 50)
            for device in battery_devices:
                print(format_device_info(device, show_services=True))
                print(f"  MAC Address: {device['address']}")
                print(
                    f"  Signal: {device['rssi']} dBm"
                    if device["rssi"]
                    else "  Signal: Unknown"
                )
                print()
        else:
            print("\nNo Li-Time battery devices found.")
            print("\nTroubleshooting tips:")
            print("- Ensure your Li-Time battery is powered on")
            print("- Make sure the battery is in range")
            print("- Check that Bluetooth is enabled on your system")
            print("- Try increasing the scan timeout")

        if battery_devices:
            print("\nExample: Automatic device selection")
            best_device = max(battery_devices, key=lambda d: d["rssi"] or -100)
            print(
                f"Best signal device: {best_device['address']} ({best_device['name']})"
            )
            print(f"  RSSI: {best_device['rssi']} dBm")
            print(
                f"  Use this address with: BatteryClient(address='{best_device['address']}')"
            )

    else:
        print("Scanning for all BLE devices...")
        all_devices = await discover_devices(timeout=timeout)

        print(f"\nFound {len(all_devices)} total devices:")
        print("-" * 50)
        for device in all_devices:
            print(format_device_info(device))


def main_sync(timeout: float, battery_only: bool, debug: bool) -> None:
    """Synchronous discovery demonstration."""
    from litime_ble import find_litime_batteries_sync

    configure_logging(DEBUG if debug else INFO)

    battery_devices = find_litime_batteries_sync(timeout=timeout)

    if battery_devices:
        print(f"Found {len(battery_devices)} Li-Time battery device(s):")
        for device in battery_devices:
            print(f"  {device['address']} - {device['name'] or 'Unknown'}")
    else:
        print("No Li-Time batteries found")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Device discovery examples")
    p.add_argument("--timeout", type=float, default=8.0, help="Scan timeout in seconds")
    p.add_argument(
        "--battery-only", action="store_true", help="Only show Li-Time battery devices"
    )
    p.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run non-interactively (use defaults and skip prompts)",
    )
    p.add_argument("--sync", action="store_true", help="Run synchronous version")
    p.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()

    if args.non_interactive:
        if args.sync:
            main_sync(
                timeout=args.timeout, battery_only=args.battery_only, debug=args.debug
            )
        else:
            asyncio.run(
                main_async(
                    timeout=args.timeout,
                    battery_only=args.battery_only,
                    debug=args.debug,
                )
            )
    else:
        # Interactive fallback for human users
        print("Choose example:")
        print("1. Async version (recommended)")
        print("2. Sync version (simpler)")

        choice = input("Enter choice (1-2): ").strip()

        if choice == "2":
            main_sync(
                timeout=args.timeout, battery_only=args.battery_only, debug=args.debug
            )
        else:
            asyncio.run(
                main_async(
                    timeout=args.timeout,
                    battery_only=args.battery_only,
                    debug=args.debug,
                )
            )
"""
Device discovery example for Li-Time BLE library.

This example demonstrates:
- Scanning for all BLE devices
- Filtering for Li-Time battery devices only
- Displaying device information including MAC addresses and service UUIDs
"""

import asyncio
from litime_ble import (
    discover_devices,
    find_litime_batteries,
    format_device_info,
    configure_logging,
    INFO,
)


async def main():
    """Demonstrate BLE device discovery functionality."""
    print("=== Li-Time BLE Device Discovery Example ===\n")

    # Enable INFO logging to see discovery progress
    configure_logging(INFO)

    # Discover all BLE devices
    print("1. Scanning for all BLE devices...")
    all_devices = await discover_devices(timeout=8.0)

    print(f"\nFound {len(all_devices)} total devices:")
    print("-" * 50)
    for device in all_devices:
        print(format_device_info(device))

    # Discover only Li-Time battery devices
    print("\n\n2. Scanning for Li-Time battery devices only...")
    battery_devices = await find_litime_batteries(timeout=8.0)

    if battery_devices:
        print(f"\nFound {len(battery_devices)} Li-Time battery device(s):")
        print("-" * 50)
        for device in battery_devices:
            print(format_device_info(device, show_services=True))
            print(f"  MAC Address: {device['address']}")
            print(
                f"  Signal: {device['rssi']} dBm"
                if device["rssi"]
                else "  Signal: Unknown"
            )
            print()
    else:
        print("\nNo Li-Time battery devices found.")
        print("\nTroubleshooting tips:")
        print("- Ensure your Li-Time battery is powered on")
        print("- Make sure the battery is in range")
        print("- Check that Bluetooth is enabled on your system")
        print("- Try increasing the scan timeout")

    # Show example of programmatic device selection
    if battery_devices:
        print("\n3. Example: Automatic device selection")
        best_device = max(battery_devices, key=lambda d: d["rssi"] or -100)
        print(f"Best signal device: {best_device['address']} ({best_device['name']})")
        print(f"  RSSI: {best_device['rssi']} dBm")
        print(
            f"  Use this address with: BatteryClient(address='{best_device['address']}')"
        )


def main_sync():
    """Synchronous wrapper for the async example."""
    print("=== Li-Time BLE Device Discovery (Sync) ===\n")

    # Import sync versions
    from litime_ble import find_litime_batteries_sync

    configure_logging(INFO)

    # This is easier for simple scripts
    battery_devices = find_litime_batteries_sync(timeout=5.0)

    if battery_devices:
        print(f"Found {len(battery_devices)} Li-Time battery device(s):")
        for device in battery_devices:
            print(f"  {device['address']} - {device['name'] or 'Unknown'}")
    else:
        print("No Li-Time batteries found")


if __name__ == "__main__":
    print("Choose example:")
    print("1. Async version (recommended)")
    print("2. Sync version (simpler)")

    choice = input("Enter choice (1-2): ").strip()

    if choice == "2":
        main_sync()
    else:
        asyncio.run(main())
