import pytest

from litime_ble.client import parse_payload
from litime_ble.models import ChargeState


def test_parse_minimal_mock():
    # Build a fake payload long enough and with fields
    buf = bytearray(70)
    # voltage 25.600 V
    buf[12:16] = (25600).to_bytes(4, "little", signed=False)
    #  current -12.345 A
    buf[48:52] = int(-12345).to_bytes(4, "little", signed=True)
    # cell temps
    buf[52:54] = int(22).to_bytes(2, "little", signed=True)
    buf[54:56] = int(24).to_bytes(2, "little", signed=True)
    # remaining 50.00 Ah, capacity 100.00 Ah
    buf[62:64] = int(5000).to_bytes(2, "little", signed=False)
    buf[64:66] = int(10000).to_bytes(2, "little", signed=False)
    # first two cells 3.300 V, 3.301 V
    buf[16:18] = int(3300).to_bytes(2, "little", signed=False)
    buf[18:20] = int(3301).to_bytes(2, "little", signed=False)

    s = parse_payload(bytes(buf))
    assert s.voltage_v == pytest.approx(25.6)
    assert s.current_a == pytest.approx(-12.345)
    assert s.soc_percent == pytest.approx(50.0)
    assert s.charge_state == ChargeState.DISCHARGING
    assert s.cell_volts_v[:2] == pytest.approx([3.3, 3.301])
