from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Optional, Iterator
from bleak import BleakClient, BleakScanner
from .models import BatteryStatus, ChargeState
from .errors import BatteryConnectionError, ProtocolError, BatteryTimeoutError


# 16-bit UUIDs expanded to 128-bit Bluetooth base
def u16(uuid16: int) -> str:
    return f"0000{uuid16:04x}-0000-1000-8000-00805f9b34fb"


SERVICE_UUID = u16(0xFFE0)
CHAR_TX_NOTIFY = u16(0xFFE1)  # notifications from battery to us
CHAR_RX_WRITE = u16(0xFFE2)  # we write requests

# Command buffer per reference JS. Little-endian 16-bit words:
# 0x0000, 0x0401, 0x1355, 0xAA17
REQUEST_STATS = bytes([0x00, 0x00, 0x01, 0x04, 0x55, 0x13, 0x17, 0xAA])

# Protocol constants
MIN_PAYLOAD_LEN = 66
MAX_RETRIES = 3


@dataclass
class BatteryClient:
    address: Optional[str] = None
    name: Optional[str] = None
    request_timeout_s: float = 5.0
    _client: Optional[BleakClient] = None

    async def connect(self) -> None:
        if not self.address and not self.name:
            raise BatteryConnectionError("Provide address or name for discovery.")
        device = None
        if self.address:
            device = await BleakScanner.find_device_by_address(
                self.address, timeout=10.0
            )
        else:
            device = await BleakScanner.find_device_by_filter(
                lambda d, _: (d.name or "").strip() == self.name, timeout=10.0
            )
        if not device:
            raise BatteryConnectionError("BLE device not found.")
        self._client = BleakClient(device)
        try:
            await self._client.connect(timeout=10.0)
            # Optional: services resolution to verify presence
            # Some BleakClient versions expose get_services; silence type check if not present
            try:
                await self._client.get_services()  # type: ignore[attr-defined]
            except (AttributeError, OSError):
                # Ignore service resolution or OS-level errors; connection succeeded
                pass
        except Exception as e:
            raise BatteryConnectionError(f"connect failed: {e}") from e

    async def disconnect(self) -> None:
        if self._client and self._client.is_connected:
            await self._client.disconnect()
        self._client = None

    @asynccontextmanager
    async def session(self) -> AsyncIterator["BatteryClient"]:
        try:
            await self.connect()
            yield self
        finally:
            await self.disconnect()

    @contextmanager
    def sync(self) -> Iterator["BatteryClient"]:
        # Synchronous context manager wrapping the async connect/disconnect
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.connect())
            try:
                yield self
            finally:
                loop.run_until_complete(self.disconnect())
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    # Sync helper: one-shot read
    def read_once(self) -> BatteryStatus:
        # Run the async read_once_async in a fresh event loop and return result
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.read_once_async())
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    async def read_once_async(self) -> BatteryStatus:
        if not self._client or not self._client.is_connected:
            raise BatteryConnectionError("Not connected.")

        q: asyncio.Queue[bytes] = asyncio.Queue()

        def _cb(_, data: bytearray):
            # push every notification; we'll filter by length
            try:
                q.put_nowait(bytes(data))
            except Exception:
                pass

        try:
            await self._client.start_notify(CHAR_TX_NOTIFY, _cb)
            # Give notifications time to set up before sending request
            await asyncio.sleep(0.1)

            try:
                # send request and wait for a full frame, allow a few retries
                for attempt in range(1, MAX_RETRIES + 1):
                    # Clear any stale notifications before sending request
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except asyncio.QueueEmpty:
                            break

                    await self._client.write_gatt_char(
                        CHAR_RX_WRITE, REQUEST_STATS, response=False
                    )

                    try:
                        # loop until timeout looking for a long payload
                        deadline = (
                            asyncio.get_event_loop().time() + self.request_timeout_s
                        )
                        while True:
                            timeout = max(0, deadline - asyncio.get_event_loop().time())
                            if timeout == 0:
                                break
                            pkt = await asyncio.wait_for(q.get(), timeout=timeout)
                            if len(pkt) >= MIN_PAYLOAD_LEN:
                                return parse_payload(pkt)
                            # else: short packet (e.g., 9 bytes). Keep waiting within this attempt.
                    except asyncio.TimeoutError:
                        # try again (re-send request)
                        if attempt == MAX_RETRIES:
                            raise BatteryTimeoutError(
                                "No full status payload received."
                            )  # fall through to finally
                        # small backoff before retry
                        await asyncio.sleep(0.2)
                # If loop ends without return, raise
                raise BatteryTimeoutError("No full status payload received.")
            finally:
                await self._client.stop_notify(CHAR_TX_NOTIFY)
        except BatteryTimeoutError:
            raise
        except Exception as e:
            raise ProtocolError(f"exchange failed: {e}") from e

    async def stream(self, interval_s: float = 3.0):
        """Async generator yielding BatteryStatus repeatedly."""
        while True:
            yield await self.read_once_async()
            await asyncio.sleep(interval_s)


def _le_u16(b: bytes, off: int) -> int:
    return int.from_bytes(b[off : off + 2], "little", signed=False)


def _le_i16(b: bytes, off: int) -> int:
    return int.from_bytes(b[off : off + 2], "little", signed=True)


def _le_u32(b: bytes, off: int) -> int:
    return int.from_bytes(b[off : off + 4], "little", signed=False)


def _le_i32(b: bytes, off: int) -> int:
    return int.from_bytes(b[off : off + 4], "little", signed=True)


def parse_payload(buf: bytes) -> BatteryStatus:
    # Guard minimal length based on highest offset used (64+2)
    if len(buf) < 66:
        raise ProtocolError(f"payload too short: {len(buf)} bytes")

    voltage = _le_u32(buf, 12) / 1000.0
    current = _le_i32(buf, 48) / 1000.0
    remaining_ah = _le_u16(buf, 62) / 100.0
    capacity_ah = _le_u16(buf, 64) / 100.0 if len(buf) >= 66 else 0.0
    soc = max(
        0.0,
        min(100.0, (remaining_ah / capacity_ah * 100.0) if capacity_ah > 0 else 0.0),
    )
    cells = []
    base = 16
    for i in range(16):
        off = base + 2 * i
        if off + 2 <= len(buf):
            v = _le_u16(buf, off)
            if v != 0:
                cells.append(v / 1000.0)
    cell_temp_c = _le_i16(buf, 52)
    bms_temp_c = _le_i16(buf, 54)
    power = voltage * current

    if current > 0:
        state = ChargeState.CHARGING
    elif current < 0:
        state = ChargeState.DISCHARGING
    else:
        state = ChargeState.IDLE

    return BatteryStatus(
        voltage_v=voltage,
        current_a=current,
        power_w=power,
        remaining_ah=remaining_ah,
        capacity_ah=capacity_ah,
        soc_percent=soc,
        cell_volts_v=cells,
        cell_temp_c=cell_temp_c,
        bms_temp_c=bms_temp_c,
        charge_state=state,
        raw=bytes(buf),
    )
