from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Optional, Iterator
from bleak import BleakClient, BleakScanner
from .models import BatteryStatus, ChargeState
from .errors import BatteryConnectionError, ProtocolError, BatteryTimeoutError
from .logging import get_logger

logger = get_logger()


# 16-bit UUIDs expanded to 128-bit Bluetooth base
def u16(uuid16: int) -> str:
    return "0000%04x-0000-1000-8000-00805f9b34fb" % uuid16


SERVICE_UUID = u16(0xFFE0)
CHAR_NOTIFY = u16(0xFFE1)  # notifications from battery to us (was CHAR_TX_NOTIFY)
CHAR_WRITE = u16(0xFFE2)  # we write requests to battery (was CHAR_RX_WRITE)

# Command buffer per reference JS. Big-endian 16-bit words:
# 0x0000, 0x0401, 0x1355, 0xAA17
REQUEST_STATS = bytes([0x00, 0x00, 0x04, 0x01, 0x13, 0x55, 0xAA, 0x17])

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
            logger.info("Connecting to battery at %s", self.address)
            device = await BleakScanner.find_device_by_address(
                self.address, timeout=10.0
            )
        else:
            logger.info("Searching for battery named '%s'", self.name)
            device = await BleakScanner.find_device_by_filter(
                lambda d, _: (d.name or "").strip() == self.name, timeout=10.0
            )

        if not device:
            logger.error(
                "Battery not found - check address/name and ensure device is powered on"
            )
            raise BatteryConnectionError("BLE device not found.")

        logger.debug("Found device: %s at %s", device.name, device.address)
        self._client = BleakClient(device)

        try:
            await self._client.connect(timeout=10.0)
            logger.info("Connected to battery %s", device.address)

            # Verify required services are available
            try:
                # Use the services property instead of deprecated get_services()
                services = self._client.services

                # Validate required characteristics exist
                if SERVICE_UUID not in [s.uuid for s in services]:
                    logger.warning(
                        "Service %s not found in device services", SERVICE_UUID
                    )
                else:
                    service = services.get_service(SERVICE_UUID)
                    if service is not None:
                        chars = [c.uuid for c in service.characteristics]
                        if CHAR_NOTIFY not in chars:
                            logger.warning(
                                "Notification characteristic %s not found", CHAR_NOTIFY
                            )
                        if CHAR_WRITE not in chars:
                            logger.warning(
                                "Write characteristic %s not found", CHAR_WRITE
                            )
                        logger.debug("Required GATT characteristics verified")
                    else:
                        logger.warning(
                            "Service %s could not be retrieved", SERVICE_UUID
                        )

            except (AttributeError, OSError) as e:
                logger.debug("Service validation skipped: %s", e)
        except Exception as e:
            logger.error("Connection failed: %s", e)
            raise BatteryConnectionError("connect failed: %s" % e) from e

    async def disconnect(self) -> None:
        if self._client and self._client.is_connected:
            await self._client.disconnect()
            logger.debug("Disconnected from battery")
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
        # Always use threaded approach to avoid any event loop conflicts
        logger.debug("Using threaded approach for sync context manager")
        import concurrent.futures

        def run_in_thread():
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Create a new client instance for the thread
                thread_client = BatteryClient(address=self.address, name=self.name)
                loop.run_until_complete(thread_client.connect())
                return thread_client, loop
            except Exception:
                loop.close()
                raise

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            thread_client, loop = future.result()

            try:
                yield thread_client
            finally:
                # Disconnect in the same thread
                def cleanup():
                    try:
                        loop.run_until_complete(thread_client.disconnect())
                    finally:
                        loop.close()

                cleanup_future = executor.submit(cleanup)
                cleanup_future.result()

    # Sync helper: one-shot read
    def read_once(self) -> BatteryStatus:
        # Check if we're already connected (for example in tests)
        if self._client and self._client.is_connected:
            # Use direct async approach if already connected
            logger.debug("Using direct async approach (already connected)")
            import asyncio

            try:
                # If there's a running loop, we can't use run_until_complete
                asyncio.get_running_loop()
                raise RuntimeError(
                    "Cannot use read_once() with existing connection when event loop is running"
                )
            except RuntimeError as e:
                if "Cannot use read_once()" in str(e):
                    raise
                # No running loop, safe to use run_until_complete
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    return loop.run_until_complete(self.read_once_async())
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)

        # Not connected, use threaded approach to avoid any event loop conflicts
        # This is especially important in ROS2 environments
        logger.debug("Using threaded approach for sync operation")
        import concurrent.futures

        def run_in_thread():
            # Create a completely isolated environment
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Create a new client instance for the thread
                client = BatteryClient(address=self.address, name=self.name)

                async def isolated_read():
                    async with client.session():
                        return await client.read_once_async()

                return loop.run_until_complete(isolated_read())
            finally:
                loop.close()
                # Don't set event loop to None in thread as it might affect other threads

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    async def read_once_async(self) -> BatteryStatus:
        if not self._client or not self._client.is_connected:
            raise BatteryConnectionError("Not connected.")

        logger.debug("Reading battery status from %s", self.address)
        q: asyncio.Queue[bytes] = asyncio.Queue()
        notification_count = 0

        def _cb(_, data: bytearray):
            nonlocal notification_count
            notification_count += 1
            data_bytes = bytes(data)

            # Log only first few notifications or important ones to avoid spam
            if notification_count <= 3 or len(data_bytes) >= MIN_PAYLOAD_LEN:
                logger.debug(
                    "Notification #%d: %d bytes", notification_count, len(data_bytes)
                )
                if len(data_bytes) >= MIN_PAYLOAD_LEN:
                    logger.debug("Full payload received: %s...", data_bytes[:16].hex())
                elif len(data_bytes) <= 16:
                    logger.debug("Short payload: %s", data_bytes.hex())

            try:
                q.put_nowait(data_bytes)
            except (asyncio.QueueFull, RuntimeError) as e:
                logger.warning("Failed to queue notification: %s", e)

        try:
            logger.debug("Setting up notifications")
            await self._client.start_notify(CHAR_NOTIFY, _cb)
            await asyncio.sleep(0.1)  # Allow notification setup

            try:
                for attempt in range(1, MAX_RETRIES + 1):
                    if attempt > 1:
                        logger.info("Retry attempt %d/%d", attempt, MAX_RETRIES)

                    # Clear stale notifications
                    cleared_count = 0
                    while not q.empty():
                        try:
                            q.get_nowait()
                            cleared_count += 1
                        except asyncio.QueueEmpty:
                            break
                    if cleared_count > 0:
                        logger.debug("Cleared %d stale notifications", cleared_count)

                    logger.debug("Sending status request: %s", REQUEST_STATS.hex())
                    await self._client.write_gatt_char(
                        CHAR_WRITE, REQUEST_STATS, response=False
                    )

                    try:
                        deadline = (
                            asyncio.get_event_loop().time() + self.request_timeout_s
                        )
                        while True:
                            timeout = max(
                                0.1, deadline - asyncio.get_event_loop().time()
                            )
                            if timeout <= 0.1:
                                logger.debug(
                                    "Timeout waiting for response (attempt %d)", attempt
                                )
                                break

                            pkt = await asyncio.wait_for(q.get(), timeout=timeout)

                            if len(pkt) >= MIN_PAYLOAD_LEN:
                                logger.info(
                                    "Battery status received (%d bytes)", len(pkt)
                                )
                                return parse_payload(pkt)
                            else:
                                logger.debug(
                                    "Waiting for full payload (got %d bytes)", len(pkt)
                                )

                    except asyncio.TimeoutError as exc:
                        if attempt == MAX_RETRIES:
                            logger.error(
                                "No response after %d attempts (timeout=%ss)",
                                MAX_RETRIES,
                                self.request_timeout_s,
                            )
                            raise BatteryTimeoutError(
                                "No full status payload received."
                            ) from exc
                        logger.warning("Attempt %d timed out, retrying...", attempt)
                        await asyncio.sleep(0.2)

                raise BatteryTimeoutError("No full status payload received.")
            finally:
                await self._client.stop_notify(CHAR_NOTIFY)
                logger.debug("Notifications stopped")
        except BatteryTimeoutError:
            raise
        except Exception as e:
            raise ProtocolError("exchange failed: %s" % e) from e

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
    logger.debug("Parsing %d-byte payload", len(buf))
    if len(buf) < 66:
        raise ProtocolError("payload too short: %d bytes" % len(buf))

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

    logger.info(
        "Battery: %.2fV %+.2fA %.0f%% (%d cells, %d°C)",
        voltage,
        current,
        soc,
        len(cells),
        cell_temp_c,
    )

    status = BatteryStatus(
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

    return status
