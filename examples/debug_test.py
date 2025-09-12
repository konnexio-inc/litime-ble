"""
Debug test script for Li-Time BLE battery communication.
This script enables detailed logging to help diagnose connection and protocol issues.
"""

import argparse
import asyncio
from typing import Optional

from litime_ble import BatteryClient, configure_logging, DEBUG


async def run(mac: str, debug: bool) -> int:
    if debug:
        configure_logging(DEBUG)

    print("Starting Li-Time BLE debug test...")
    print(f"Target device: {mac}")

    client = BatteryClient(address=mac)

    try:
        async with client.session():
            print("Connected successfully!")
            print("Attempting to read battery status...")
            status = await client.read_once_async()
            print("\n=== BATTERY STATUS ===")
            print(status.json())
            print("======================")

    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Debug test for Li-Time BLE")
    p.add_argument("--mac", default="C8:47:80:15:5C:0F", help="Battery MAC address")
    p.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    code = asyncio.run(run(args.mac, args.debug))
    raise SystemExit(code)
