class BatteryError(Exception):
    """Base error for litime-ble."""


class BatteryConnectionError(BatteryError):
    """BLE connection or discovery failure."""


class ProtocolError(BatteryError):
    """Unexpected packet structure or parse failure."""


class BatteryTimeoutError(BatteryError):
    """Timeout waiting for notification or operation."""
