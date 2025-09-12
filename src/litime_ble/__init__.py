from .client import BatteryClient
from .models import BatteryStatus, ChargeState
from .errors import (
    BatteryError,
    BatteryConnectionError,
    ProtocolError,
    BatteryTimeoutError,
)
from .logging import configure_logging, DEBUG, INFO, WARNING, ERROR
from .discovery import (
    discover_devices,
    discover_devices_sync,
    find_litime_batteries,
    find_litime_batteries_sync,
    format_device_info,
)

__version__ = "0.2.1"

__all__ = [
    "BatteryClient",
    "BatteryStatus",
    "ChargeState",
    "BatteryError",
    "BatteryConnectionError",
    "ProtocolError",
    "BatteryTimeoutError",
    "configure_logging",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "discover_devices",
    "discover_devices_sync",
    "find_litime_batteries",
    "find_litime_batteries_sync",
    "format_device_info",
    "__version__",
]
