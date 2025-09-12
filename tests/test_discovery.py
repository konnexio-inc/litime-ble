"""Tests for BLE device discovery functionality."""

import pytest
from unittest.mock import patch, AsyncMock

from litime_ble.discovery import (
    discover_devices,
    discover_devices_sync,
    find_litime_batteries,
    format_device_info,
)


class MockBLEDevice:
    def __init__(self, address: str, name: str | None = None):
        self.address = address
        self.name = name


class MockAdvData:
    def __init__(self, rssi: int = -50, service_uuids=None):
        self.rssi = rssi
        self.service_uuids = service_uuids or []


@pytest.mark.asyncio
async def test_discover_devices():
    """Test basic device discovery."""
    mock_devices = [
        MockBLEDevice("AA:BB:CC:DD:EE:01", "Li-Time Battery 1"),
        MockBLEDevice("AA:BB:CC:DD:EE:02", "Test Device 2"),
        MockBLEDevice("AA:BB:CC:DD:EE:03"),
    ]

    with patch(
        "litime_ble.discovery.BleakScanner.discover", new_callable=AsyncMock
    ) as mock_discover:
        mock_discover.return_value = mock_devices

        devices = await discover_devices(timeout=5.0)

        assert len(devices) == 3
        assert devices[0]["address"] == "AA:BB:CC:DD:EE:01"
        assert devices[0]["name"] == "Li-Time Battery 1"
        assert devices[0]["rssi"] is None  # Not available in basic discovery
        assert devices[0]["is_litime_battery"] is True  # Detected by name

        assert devices[1]["address"] == "AA:BB:CC:DD:EE:02"
        assert devices[1]["is_litime_battery"] is False


@pytest.mark.asyncio
async def test_find_litime_batteries():
    """Test finding only battery devices."""
    mock_devices = [
        MockBLEDevice("AA:BB:CC:DD:EE:01", "Li-Time Battery"),
        MockBLEDevice("AA:BB:CC:DD:EE:02", "Other Device"),
    ]

    with patch(
        "litime_ble.discovery.BleakScanner.discover", new_callable=AsyncMock
    ) as mock_discover:
        mock_discover.return_value = mock_devices

        devices = await find_litime_batteries(timeout=5.0)

        assert len(devices) == 1
        assert devices[0]["address"] == "AA:BB:CC:DD:EE:01"
        assert devices[0]["is_litime_battery"] is True


def test_discover_devices_sync():
    """Test synchronous device discovery."""
    mock_devices = [
        MockBLEDevice("AA:BB:CC:DD:EE:01", "Test Device"),
    ]

    with patch(
        "litime_ble.discovery.BleakScanner.discover", new_callable=AsyncMock
    ) as mock_discover:
        mock_discover.return_value = mock_devices

        devices = discover_devices_sync(timeout=5.0)

        assert len(devices) == 1
        assert devices[0]["address"] == "AA:BB:CC:DD:EE:01"


def test_format_device_info():
    """Test device info formatting."""
    device = {
        "address": "AA:BB:CC:DD:EE:FF",
        "name": "Test Battery",
        "rssi": -45,
        "services": ["0000ffe0-0000-1000-8000-00805f9b34fb", "other-service"],
        "is_litime_battery": True,
    }

    # Basic format
    formatted = format_device_info(device)
    assert "AA:BB:CC:DD:EE:FF" in formatted
    assert "Test Battery" in formatted
    assert "RSSI: -45" in formatted
    assert "[Li-Time Battery]" in formatted

    # With services
    formatted_with_services = format_device_info(device, show_services=True)
    assert "Services:" in formatted_with_services
    assert "0000ffe0" in formatted_with_services


def _is_litime_battery_name(device_name: str | None) -> bool:
    """Helper function to test battery name detection logic."""
    if not device_name:
        return False

    device_name = device_name.lower()
    return (
        "li-time" in device_name
        or "litime" in device_name
        or "battery" in device_name
        or device_name.startswith(
            "l-"
        )  # Li-Time battery naming pattern (case insensitive)
        or "gbn" in device_name  # Common in Li-Time model numbers
    )


def test_battery_detection_patterns():
    """Test battery detection with various naming patterns."""
    test_cases = [
        # Original patterns
        ("Li-Time Battery", True),
        ("LiTime", True),
        ("li-time", True),
        ("LITIME", True),
        ("Battery Pack", True),
        # New patterns with L- prefix
        ("L-51100GBN250-A00441", True),
        ("L-12V100", True),
        ("L-something", True),
        # GBN patterns (case insensitive)
        ("51100GBN250", True),
        ("12v100gbn", True),
        ("TestGBNDevice", True),
        # Non-matching patterns
        ("Random Device", False),
        ("L", False),  # Too short
        ("GBN", True),  # This should match
        (None, False),  # No name
        ("", False),  # Empty name
    ]

    for name, expected in test_cases:
        is_detected = _is_litime_battery_name(name)
        assert is_detected == expected, (
            f"Name '{name}' should {'be' if expected else 'not be'} detected as Li-Time battery"
        )


def test_format_device_info_no_name():
    """Test formatting device with no name."""
    device = {
        "address": "AA:BB:CC:DD:EE:FF",
        "name": None,
        "rssi": None,
        "services": [],
        "is_litime_battery": False,
    }

    formatted = format_device_info(device)
    assert "AA:BB:CC:DD:EE:FF" in formatted
    assert "Unknown" in formatted
    assert "[Li-Time Battery]" not in formatted
