import pytest

from litime_ble.client import parse_payload
from litime_ble.errors import ProtocolError
from litime_ble.models import ChargeState


def make_base_buffer():
    """Return a base bytearray of length 70 initialized with zeros."""
    return bytearray(70)


def test_parse_happy_path():
    buf = make_base_buffer()
    # voltage 25.600 V
    buf[12:16] = (25600).to_bytes(4, "little", signed=False)
    # current -12.345 A
    buf[48:52] = int(-12345).to_bytes(4, "little", signed=True)
    # temps
    buf[52:54] = int(22).to_bytes(2, "little", signed=True)
    buf[54:56] = int(24).to_bytes(2, "little", signed=True)
    # remaining 50.00 Ah, capacity 100.00 Ah
    buf[62:64] = int(5000).to_bytes(2, "little", signed=False)
    buf[64:66] = int(10000).to_bytes(2, "little", signed=False)
    # first cells
    buf[16:18] = int(3300).to_bytes(2, "little", signed=False)
    buf[18:20] = int(3301).to_bytes(2, "little", signed=False)

    s = parse_payload(bytes(buf))
    assert s.voltage_v == pytest.approx(25.6)
    assert s.current_a == pytest.approx(-12.345)
    assert s.soc_percent == pytest.approx(50.0)
    assert s.charge_state == ChargeState.DISCHARGING
    assert s.cell_volts_v[:2] == pytest.approx([3.3, 3.301])


def test_short_buffer_raises():
    with pytest.raises(ProtocolError):
        parse_payload(b"\x00\x01")


def test_capacity_zero_leads_to_soc_zero():
    buf = make_base_buffer()
    buf[12:16] = (12000).to_bytes(4, "little", signed=False)
    buf[48:52] = (0).to_bytes(4, "little", signed=True)
    buf[62:64] = int(1000).to_bytes(2, "little", signed=False)  # remaining
    buf[64:66] = int(0).to_bytes(2, "little", signed=False)  # capacity zero

    s = parse_payload(bytes(buf))
    assert s.capacity_ah == pytest.approx(0.0)
    assert s.soc_percent == pytest.approx(0.0)


def test_current_sign_sets_charge_state():
    buf = make_base_buffer()
    buf[12:16] = (12000).to_bytes(4, "little", signed=False)
    # positive current -> charging
    buf[48:52] = int(5000).to_bytes(4, "little", signed=True)
    buf[62:64] = int(1000).to_bytes(2, "little", signed=False)
    buf[64:66] = int(2000).to_bytes(2, "little", signed=False)
    s = parse_payload(bytes(buf))
    assert s.charge_state == ChargeState.CHARGING

    # negative current -> discharging
    buf[48:52] = int(-5000).to_bytes(4, "little", signed=True)
    s = parse_payload(bytes(buf))
    assert s.charge_state == ChargeState.DISCHARGING

    # zero current -> idle
    buf[48:52] = (0).to_bytes(4, "little", signed=True)
    s = parse_payload(bytes(buf))
    assert s.charge_state == ChargeState.IDLE


def test_zero_cells_ignored():
    buf = make_base_buffer()
    buf[12:16] = (12000).to_bytes(4, "little", signed=False)
    # first cell zero, second non-zero
    buf[16:18] = (0).to_bytes(2, "little", signed=False)
    buf[18:20] = int(3300).to_bytes(2, "little", signed=False)
    buf[62:64] = int(1000).to_bytes(2, "little", signed=False)
    buf[64:66] = int(2000).to_bytes(2, "little", signed=False)

    s = parse_payload(bytes(buf))
    assert s.cell_volts_v == pytest.approx([3.3])
