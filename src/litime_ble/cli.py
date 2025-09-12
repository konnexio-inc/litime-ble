from __future__ import annotations
import argparse
from .client import BatteryClient


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="litime-battery", description="Read Li Time BLE battery"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    rd = sub.add_parser("read", help="Read once")
    rd.add_argument("--address", help="BLE MAC")
    rd.add_argument("--name", help="BLE device name")
    rd.add_argument("--json", action="store_true", help="Output JSON")

    args = ap.parse_args()

    if args.cmd == "read":
        client = BatteryClient(address=args.address, name=args.name)
        with client.sync() as c:
            s = c.read_once()
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
