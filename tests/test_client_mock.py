import asyncio
import threading
import time

import pytest

from litime_ble.client import BatteryClient
from litime_ble.errors import BatteryConnectionError, BatteryTimeoutError


@pytest.mark.asyncio
async def test_connect_and_disconnect_async():
    c = BatteryClient(address="FA:KE:DD:RE:SS")
    # Should be able to connect and disconnect without raising
    await c.connect()
    assert c._client is not None and c._client.is_connected
    await c.disconnect()
    assert c._client is None or not c._client.is_connected


def test_sync_connect_disconnect():
    c = BatteryClient(address="FA:KE:DD:RE:SS")
    with c.sync() as cli:
        assert cli._client is not None and cli._client.is_connected


def test_read_once_sync(payload_builder):
    payload = payload_builder(
        voltage_mv=25600,
        current_ma=-12345,
        cell_volts_mv=[3300, 3301],
        remaining_ah_x100=5000,
        capacity_ah_x100=10000,
    )
    c = BatteryClient(address="FA:KE:DD:RE:SS")
    # Prepare the fake client to supply the payload when written to
    # Use sync context to connect
    with c.sync() as cli:
        # set the next payload that the fake client will send on write
        cli._client.next_payload = payload  # type: ignore[attr-defined]
        s = cli.read_once()
    assert s.voltage_v == pytest.approx(25.6)
    assert s.current_a == pytest.approx(-12.345)


@pytest.mark.asyncio
async def test_read_once_async_and_timeout(payload_builder):
    payload = payload_builder(voltage_mv=12000)
    c = BatteryClient(
        address="FA:KE:DD:RE:SS", request_timeout_s=0.5
    )  # Increased from 0.1
    await c.connect()
    try:
        # don't set next_payload, so read_once_async should timeout
        with pytest.raises(BatteryTimeoutError):
            await c.read_once_async()
        # now set a payload and it should succeed
        c._client.next_payload = payload  # type: ignore[attr-defined]
        s = await c.read_once_async()
        assert s.voltage_v == pytest.approx(12.0)
    finally:
        await c.disconnect()


def _read_once_bounded(client, loop=None, timeout=5.0):
    """Call read_once() so that a regression to blocking fails instead of hanging.

    With ``loop`` the call runs on that loop's own thread, otherwise on a new one.
    """
    result = []
    done = threading.Event()

    def target():
        try:
            result.append(client.read_once())
        except Exception as e:
            result.append(e)
        finally:
            done.set()

    if loop is None:
        threading.Thread(target=target, daemon=True).start()
    else:
        loop.call_soon_threadsafe(target)
    assert done.wait(timeout), "read_once() blocked instead of raising"
    return result[0]


def _sync_threads():
    return [t for t in threading.enumerate() if t.name == "litime-ble-sync"]


def test_sync_reads_repeatedly(payload_builder):
    c = BatteryClient(address="FA:KE:DD:RE:SS")
    with c.sync() as cli:
        cli._client.next_payload = payload_builder(voltage_mv=12000)  # type: ignore[attr-defined]
        first = cli.read_once()
        cli._client.next_payload = payload_builder(voltage_mv=13000)  # type: ignore[attr-defined]
        second = cli.read_once()
    assert first.voltage_v == pytest.approx(12.0)
    assert second.voltage_v == pytest.approx(13.0)


def test_sync_keeps_client_settings():
    c = BatteryClient(address="FA:KE:DD:RE:SS", request_timeout_s=0.2)
    with c.sync() as cli:
        assert cli.request_timeout_s == 0.2
        # no payload queued, so the read times out; the error crosses the thread as-is
        with pytest.raises(BatteryTimeoutError):
            cli.read_once()


def test_sync_cleans_up_on_exit():
    c = BatteryClient(address="FA:KE:DD:RE:SS")
    with c.sync() as cli:
        fake = cli._client
        assert _sync_threads()
    assert not fake.is_connected
    assert c._client is None
    assert not _sync_threads()


def test_sync_cleans_up_when_body_raises():
    c = BatteryClient(address="FA:KE:DD:RE:SS")
    with pytest.raises(ValueError):
        with c.sync() as cli:
            fake = cli._client
            raise ValueError("boom")
    assert not fake.is_connected
    assert not _sync_threads()


def test_sync_cleans_up_when_connect_fails(monkeypatch):
    import litime_ble.client as client_mod

    async def not_found(address, timeout=10.0):
        return None

    monkeypatch.setattr(
        client_mod.BleakScanner, "find_device_by_address", staticmethod(not_found)
    )
    c = BatteryClient(address="FA:KE:DD:RE:SS")
    with pytest.raises(BatteryConnectionError):
        with c.sync():
            pass
    assert not _sync_threads()


def test_read_once_refuses_to_block_the_connection_loop():
    # Called on the loop's own thread, read_once() would wait on itself forever.
    c = BatteryClient(address="FA:KE:DD:RE:SS")
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    try:
        asyncio.run_coroutine_threadsafe(c.connect(), loop).result()
        assert isinstance(_read_once_bounded(c, loop), RuntimeError)
        asyncio.run_coroutine_threadsafe(c.disconnect(), loop).result()
    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=5)
        if not thread.is_alive():
            loop.close()


def test_read_once_refuses_connection_from_stopped_loop():
    # Scheduling onto a loop that is not running would wait forever.
    c = BatteryClient(address="FA:KE:DD:RE:SS")
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(c.connect())
        assert isinstance(_read_once_bounded(c), RuntimeError)
    finally:
        loop.close()


def test_unconnected_read_once_keeps_request_timeout():
    # No payload queued, so every attempt times out: 3 x 0.2 s, not 3 x 5 s.
    c = BatteryClient(address="FA:KE:DD:RE:SS", request_timeout_s=0.2)
    t0 = time.monotonic()
    with pytest.raises(BatteryTimeoutError):
        c.read_once()
    assert time.monotonic() - t0 < 4.0
