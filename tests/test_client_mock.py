import pytest

from litime_ble.client import BatteryClient
from litime_ble.errors import BatteryTimeoutError


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
    c = BatteryClient(address="FA:KE:DD:RE:SS", request_timeout_s=0.1)
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
