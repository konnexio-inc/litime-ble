"""Logging configuration for litime_ble library."""

import logging
from typing import Union, Optional

# Create a logger for this library
logger = logging.getLogger("litime_ble")

# Logging levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR


def configure_logging(
    level: Union[int, str] = WARNING, format_string: Optional[str] = None
) -> None:
    """Configure logging for the litime_ble library.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR) or string equivalent
        format_string: Custom format string for log messages
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure the logger
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    logger.debug("Logging configured at level %s", logging.getLevelName(level))


def get_logger() -> logging.Logger:
    """Get the litime_ble logger instance."""
    return logger


def format_hex(data: bytes, max_len: int = 32) -> str:
    """Format bytes as hex string, truncating if too long."""
    if len(data) <= max_len:
        return data.hex()
    return f"{data[:max_len].hex()}... ({len(data)} bytes total)"


# Pre-configure with WARNING level by default
configure_logging(WARNING)
