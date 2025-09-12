from typing import List, Optional

import pytest


@pytest.fixture(autouse=True)
def suppress_logging():
    """Suppress logging during tests to keep output clean."""
    import litime_ble

    # Set to ERROR level to suppress DEBUG/INFO/WARNING during tests
    litime_ble.configure_logging(litime_ble.ERROR)
    yield


def build_payload(
    voltage_mv: int = 12000,
    current_ma: int = 0,
    remaining_ah_x100: int = 1000,
    capacity_ah_x100: int = 2000,
    cell_volts_mv: Optional[List[int]] = None,
    cell_temp_c: int = 22,
    bms_temp_c: int = 24,
) -> bytes:
    """Build a byte payload matching offsets used by parse_payload.

    voltage_mv: millivolts (uint32 at 12)
    current_ma: milliamps (int32 at 48)
    remaining_ah_x100: remaining Ah * 100 (uint16 at 62)
    capacity_ah_x100: capacity Ah * 100 (uint16 at 64)
    cell_volts_mv: list of cell millivolts to place starting at offset 16
    """
    if cell_volts_mv is None:
        cell_volts_mv = []
    buf = bytearray(70)
    buf[12:16] = int(voltage_mv).to_bytes(4, "little", signed=False)
    buf[48:52] = int(current_ma).to_bytes(4, "little", signed=True)
    buf[52:54] = int(cell_temp_c).to_bytes(2, "little", signed=True)
    buf[54:56] = int(bms_temp_c).to_bytes(2, "little", signed=True)
    buf[62:64] = int(remaining_ah_x100).to_bytes(2, "little", signed=False)
    buf[64:66] = int(capacity_ah_x100).to_bytes(2, "little", signed=False)

    base = 16
    for i, mv in enumerate(cell_volts_mv):
        if i >= 16:
            break
        off = base + 2 * i
        buf[off : off + 2] = int(mv).to_bytes(2, "little", signed=False)

    return bytes(buf)


class FakeBleakClient:
    def __init__(self, device=None):
        self.device = device
        self.is_connected = False
        self._notify_callback = None
        self.next_payload = None
        # Mock services for GATT validation
        self.services = {"0000ffe0-0000-1000-8000-00805f9b34fb": FakeService()}

    async def connect(self, timeout: Optional[float] = None):
        self.is_connected = True

    async def disconnect(self):
        self.is_connected = False

    async def get_services(self):
        return self.services

    async def start_notify(self, char, callback):
        # store the callback; callback signature: (sender, bytearray)
        self._notify_callback = callback

    async def stop_notify(self, char):
        self._notify_callback = None

    async def write_gatt_char(self, char, data, response: bool = False):
        # simulate device response by calling the notification callback if payload available
        # call synchronously to mimic notification arrival
        if self.next_payload is not None and self._notify_callback is not None:
            # the real Bleak callback provides sender and a bytearray
            self._notify_callback(None, bytearray(self.next_payload))


class FakeService:
    def __init__(self):
        self.uuid = "0000ffe0-0000-1000-8000-00805f9b34fb"
        self.characteristics = [
            FakeCharacteristic("0000ffe1-0000-1000-8000-00805f9b34fb"),
            FakeCharacteristic("0000ffe2-0000-1000-8000-00805f9b34fb"),
        ]


class FakeCharacteristic:
    def __init__(self, uuid: str):
        self.uuid = uuid


class FakeDevice:
    def __init__(self, address: str = "FA:KE:DD:RE:SS"):
        self.address = address
        self.name = "FakeDevice"


class FakeBleakScanner:
    @staticmethod
    async def find_device_by_address(address: str, timeout: float = 10.0):
        return FakeDevice(address)

    @staticmethod
    async def find_device_by_filter(filter_func, timeout: float = 10.0):
        # return a fake device when called
        return FakeDevice("FA:KE:FL:TR:00")


@pytest.fixture(autouse=True)
def patch_bleak(monkeypatch):
    """Autouse fixture to replace BleakClient and BleakScanner in the client module with fakes."""
    import litime_ble.client as client_mod

    monkeypatch.setattr(client_mod, "BleakClient", FakeBleakClient)
    monkeypatch.setattr(client_mod, "BleakScanner", FakeBleakScanner)
    yield


@pytest.fixture
def payload_builder():
    return build_payload
