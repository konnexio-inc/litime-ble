from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any
import json


class ChargeState(str, Enum):
    IDLE = "idle"
    CHARGING = "charging"
    DISCHARGING = "discharging"


@dataclass(slots=True)
class BatteryStatus:
    voltage_v: float
    current_a: float
    power_w: float
    remaining_ah: float
    capacity_ah: float
    soc_percent: float
    cell_volts_v: List[float]
    cell_temp_c: float
    bms_temp_c: float
    charge_state: ChargeState
    raw: bytes = field(repr=False, default=b"")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("raw", None)
        return d

    def json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), ensure_ascii=False)
