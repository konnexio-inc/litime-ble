"""
Example: Synchronous battery reading (simpler version).

This example demonstrates:
- Simple synchronous battery reading
- Basic error handling
- Easy-to-understand code for quick testing
"""

import argparse
from typing import Optional

from litime_ble import BatteryClient, configure_logging, DEBUG


def run(mac: str, debug: bool) -> int:
    if debug:
        configure_logging(DEBUG)

    print("=== Li-Time BLE Battery Reader (Sync) ===")
    print(f"Target device: {mac}")
    print()

    try:
        print("Connecting to battery...")
        client = BatteryClient(address=mac)

        with client.sync() as c:
            print("✓ Connected successfully!")

            print("Reading battery status...")
            status = c.read_once()

            print("\n--- Battery Status ---")
            print(f"Voltage:        {status.voltage_v:.3f} V")
            print(f"Current:        {status.current_a:.3f} A")
            print(f"Power:          {status.power_w:.2f} W")
            print(f"State of Charge: {status.soc_percent:.1f}%")
            print(f"Remaining:      {status.remaining_ah:.2f} Ah")
            print(f"Capacity:       {status.capacity_ah:.2f} Ah")
            print(f"Charge State:   {status.charge_state.value}")
            print(
                f"Cell Voltages:  {', '.join(f'{v:.3f}V' for v in status.cell_volts_v)}"
            )
            print(f"Cell Temp:      {status.cell_temp_c}°C")
            print(f"BMS Temp:       {status.bms_temp_c}°C")

            print("\n--- JSON Output ---")
            print(status.json())

        print("\n✓ Read completed successfully!")

    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check that your device MAC address is correct")
        print("2. Ensure the battery is powered on and in range")
        print("3. Verify Bluetooth is enabled on your system")
        print("4. Try running with administrator/sudo privileges")
        print("5. Check that no other device is connected to the battery")
        print("6. Try enabling debug logging: configure_logging(DEBUG)")
        return 1

    return 0


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sync battery read example")
    p.add_argument("--mac", default="C8:47:80:15:5C:0F", help="Battery MAC address")
    p.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(run(args.mac, args.debug))
