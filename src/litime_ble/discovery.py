"""BLE device discovery utilities for development and diagnostics."""

from __future__ import annotations
import asyncio
from typing import List, Dict, Any
from bleak import BleakScanner
from .logging import get_logger

logger = get_logger()


async def discover_devices(
    timeout: float = 10.0, include_battery_only: bool = False
) -> List[Dict[str, Any]]:
    """Discover available BLE devices.

    Args:
        timeout: Scan timeout in seconds
        include_battery_only: If True, only return devices with battery service UUID

    Returns:
        List of device info dictionaries with keys:
        - address: MAC address
        - name: Device name (may be None)
        - rssi: Signal strength (None if not available)
        - services: List of service UUIDs (empty if not available)
        - is_litime_battery: Whether device advertises Li-Time battery service
    """
    logger.debug("Starting BLE device discovery (timeout=%.1fs)", timeout)

    # Use basic discovery for now to avoid type issues
    devices = await BleakScanner.discover(timeout=timeout, return_adv=False)
    device_list = []

    for device in devices:
        # Create a scanner to try to get more info about each device
        # For now, we'll just mark devices as potential batteries based on name
        device_name = device.name or ""
        is_litime_battery = (
            "li-time" in device_name.lower()
            or "litime" in device_name.lower()
            or "battery" in device_name.lower()
            or device_name.startswith("L-")  # Li-Time battery naming pattern
            or "gbn" in device_name.lower()  # Common in Li-Time model numbers
        )

        # Skip non-battery devices if filter is enabled
        if include_battery_only and not is_litime_battery:
            continue

        device_info = {
            "address": device.address,
            "name": device.name,
            "rssi": None,  # Not available in basic discovery
            "services": [],  # Not available in basic discovery
            "is_litime_battery": is_litime_battery,
        }

        device_list.append(device_info)

        logger.debug(
            "Found device: %s (%s) battery=%s",
            device.address,
            device.name or "Unknown",
            is_litime_battery,
        )

    logger.info("Discovery complete: found %d devices", len(device_list))
    return sorted(device_list, key=lambda d: d["address"])


def discover_devices_sync(
    timeout: float = 10.0, include_battery_only: bool = False
) -> List[Dict[str, Any]]:
    """Synchronous wrapper for discover_devices()."""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(
            discover_devices(timeout=timeout, include_battery_only=include_battery_only)
        )
    finally:
        loop.close()
        asyncio.set_event_loop(None)


def format_device_info(device: Dict[str, Any], show_services: bool = False) -> str:
    """Format device info for human-readable display."""
    name = device["name"] or "Unknown"
    rssi_str = f" (RSSI: {device['rssi']})" if device["rssi"] is not None else ""
    battery_str = " [Li-Time Battery]" if device["is_litime_battery"] else ""

    result = f"{device['address']} - {name}{rssi_str}{battery_str}"

    if show_services and device["services"]:
        services_str = ", ".join(device["services"][:3])  # Show first 3 services
        if len(device["services"]) > 3:
            services_str += f" (+{len(device['services']) - 3} more)"
        result += f"\n  Services: {services_str}"

    return result


async def find_litime_batteries(timeout: float = 10.0) -> List[Dict[str, Any]]:
    """Find devices that advertise Li-Time battery service.

    This is a convenience function equivalent to:
    discover_devices(timeout=timeout, include_battery_only=True)
    """
    return await discover_devices(timeout=timeout, include_battery_only=True)


def find_litime_batteries_sync(timeout: float = 10.0) -> List[Dict[str, Any]]:
    """Synchronous wrapper for find_litime_batteries()."""
    return discover_devices_sync(timeout=timeout, include_battery_only=True)
