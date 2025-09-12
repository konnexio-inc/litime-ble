"""
Professional logging test for Li-Time BLE library.

This script tests the logging infrastructure and demonstrates proper usage
for debugging connection and protocol issues.
"""

import argparse
import asyncio
import sys
from typing import Optional

from litime_ble import BatteryClient, configure_logging, DEBUG, INFO, WARNING


async def demo_battery_connection(mac: str, request_timeout_s: float = 3.0) -> bool:
    """Demo battery connection with comprehensive logging."""

    print("=== Li-Time BLE Professional Test ===")
    print(f"Target: {mac}")
    print(f"Python: {sys.version.split()[0]}")
    print()

    # Test different logging levels
    for level_name, level in [("INFO", INFO), ("DEBUG", DEBUG)]:
        print(f"--- Testing with {level_name} logging ---")
        configure_logging(level)

        client = BatteryClient(address=mac, request_timeout_s=request_timeout_s)

        try:
            async with client.session():
                status = await client.read_once_async()
                print(
                    f"✓ Success: {status.voltage_v:.2f}V, {status.soc_percent:.0f}% SOC"
                )

                if level == DEBUG:
                    print("--- Raw Data Analysis ---")
                    print(f"Raw payload: {len(status.raw)} bytes")
                    print(
                        f"Cell voltages: {[f'{v:.3f}V' for v in status.cell_volts_v[:4]]}"
                    )
                    print(
                        f"Temperatures: Cell={status.cell_temp_c}°C, BMS={status.bms_temp_c}°C"
                    )

                break  # Success, don't test other levels

        except Exception as e:
            print(f"✗ Failed with {level_name}: {type(e).__name__}: {e}")
            if level_name == "DEBUG":
                print("\nThis detailed log should help diagnose the issue.")
                return False
            continue

    print("\n✓ All tests completed successfully!")
    return True


def demo_logging_levels():
    """Demonstrate logging level configuration."""
    print("=== Testing Logging Levels ===")

    from litime_ble.logging import get_logger

    logger = get_logger()

    for level_name, level in [("WARNING", WARNING), ("INFO", INFO), ("DEBUG", DEBUG)]:
        print(f"\n--- {level_name} Level ---")
        configure_logging(level)

        logger.debug("This is a DEBUG message")
        logger.info("This is an INFO message")
        logger.warning("This is a WARNING message")
        logger.error("This is an ERROR message")


async def main_async(mac: str, request_timeout_s: float, debug: bool) -> int:
    print("Testing logging infrastructure...")
    demo_logging_levels()

    print("\n" + "=" * 50)
    success = await demo_battery_connection(
        mac=mac, request_timeout_s=request_timeout_s
    )

    if not success:
        print("\n=== Troubleshooting Guide ===")
        print("1. Verify MAC address is correct")
        print("2. Ensure battery is powered on and nearby")
        print("3. Check no other device is connected")
        print("4. Try running with sudo/administrator privileges")
        print("5. Verify Bluetooth adapter is working")
        return 1

    return 0


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Logging and battery demo")
    p.add_argument("--mac", default="C8:47:80:15:5C:0F", help="Battery MAC address")
    p.add_argument(
        "--request-timeout", type=float, default=3.0, help="Request timeout seconds"
    )
    p.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    return p.parse_args(argv)


if __name__ == "__main__":
    try:
        args = parse_args()
        if args.debug:
            configure_logging(DEBUG)

        exit_code = asyncio.run(main_async(args.mac, args.request_timeout, args.debug))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {type(e).__name__}: {e}")
        sys.exit(1)
