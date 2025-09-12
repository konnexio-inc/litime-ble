"""
Example: Async battery reading with comprehensive error handling and logging.

This example demonstrates:
- Basic async battery reading
- Error handling
- Optional debug logging
- Multiple read attempts for testing reliability
"""

import argparse
import asyncio
import sys
from typing import Optional

from litime_ble import BatteryClient, configure_logging, DEBUG


async def run(mac: str, debug: bool) -> int:
    if debug:
        configure_logging(DEBUG)

    print("=== Li-Time BLE Battery Reader (Async) ===")
    print(f"Target device: {mac}")
    print(f"Python version: {sys.version}")
    print()

    client = BatteryClient(address=mac)

    try:
        print("Connecting to battery...")
        async with client.session():
            print("✓ Connected successfully!")

            # Perform multiple reads to test reliability
            for i in range(3):
                print(f"\n--- Read {i + 1}/3 ---")
                try:
                    status = await client.read_once_async()

                    # Display key metrics
                    print(f"Voltage:     {status.voltage_v:.3f} V")
                    print(f"Current:     {status.current_a:.3f} A")
                    print(f"Power:       {status.power_w:.2f} W")
                    print(f"State of Charge: {status.soc_percent:.1f}%")
                    print(f"Remaining:   {status.remaining_ah:.2f} Ah")
                    print(f"Capacity:    {status.capacity_ah:.2f} Ah")
                    print(f"Charge State: {status.charge_state.value}")
                    print(f"Cell Count:  {len(status.cell_volts_v)}")
                    print(
                        f"Temperatures: Cell={status.cell_temp_c}°C, BMS={status.bms_temp_c}°C"
                    )

                    if i < 2:  # Don't wait after last read
                        print("Waiting 1 second...")
                        await asyncio.sleep(1)

                except Exception as e:
                    print(f"✗ Read {i + 1} failed: {type(e).__name__}: {e}")
                    if i < 2:
                        print("Retrying...")
                        await asyncio.sleep(1)
                    else:
                        raise

            print("\n✓ All reads completed successfully!")

            # Optional: Show full JSON output
            print("\n--- Full JSON Output ---")
            final_status = await client.read_once_async()
            print(final_status.json())

    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check that your device MAC address is correct")
        print("2. Ensure the battery is powered on and in range")
        print("3. Verify Bluetooth is enabled on your system")
        print("4. Try running with administrator/sudo privileges")
        print("5. Check that no other device is connected to the battery")
        return 1

    return 0


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Async battery read example")
    p.add_argument("--mac", default="C8:47:80:15:5C:0F", help="Battery MAC address")
    p.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    code = asyncio.run(run(args.mac, args.debug))
    sys.exit(code)
