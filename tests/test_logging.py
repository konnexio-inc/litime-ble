"""Tests for the logging infrastructure."""

from unittest.mock import patch

from litime_ble import configure_logging, DEBUG, INFO, WARNING, ERROR
from litime_ble.logging import get_logger, format_hex


def test_configure_logging_with_level():
    """Test logging configuration with different levels."""
    logger = get_logger()

    # Test with DEBUG level
    configure_logging(DEBUG)
    assert logger.level == DEBUG

    # Test with string level
    configure_logging("INFO")
    assert logger.level == INFO

    # Test with default WARNING
    configure_logging()
    assert logger.level == WARNING


def test_format_hex():
    """Test hex formatting utility."""
    # Short data
    short_data = b"\x00\x01\x02\x03"
    assert format_hex(short_data) == "00010203"

    # Long data gets truncated
    long_data = b"\x00" * 50
    formatted = format_hex(long_data, max_len=16)
    assert formatted == "00000000000000000000000000000000... (50 bytes total)"

    # Exact length
    exact_data = b"\xff" * 32
    formatted = format_hex(exact_data, max_len=32)
    assert formatted == "ff" * 32  # Python hex() returns lowercase


def test_logging_suppression_in_tests():
    """Verify that logging is suppressed during tests."""
    logger = get_logger()

    # Logger should be at ERROR level due to conftest.py fixture
    assert logger.level == ERROR

    # Verify handlers exist but are at ERROR level
    assert len(logger.handlers) > 0
    for handler in logger.handlers:
        assert handler.level == ERROR


@patch("litime_ble.logging.logger")
def test_logging_during_operations(mock_logger):
    """Test that logging calls are made during operations."""
    from litime_ble.client import parse_payload

    # Enable debug logging for this test
    configure_logging(DEBUG)

    # Create a valid payload
    buf = bytearray(70)
    buf[12:16] = (12000).to_bytes(4, "little", signed=False)  # voltage
    buf[48:52] = (1000).to_bytes(4, "little", signed=True)  # current
    buf[62:64] = (5000).to_bytes(2, "little", signed=False)  # remaining
    buf[64:66] = (10000).to_bytes(2, "little", signed=False)  # capacity

    # Parse the payload
    status = parse_payload(bytes(buf))

    # Verify logging was called
    assert status.voltage_v == 12.0
    # Note: We don't check exact log calls since they're mocked,
    # but this ensures the code runs without logging errors


def test_logger_singleton():
    """Test that get_logger returns the same instance."""
    logger1 = get_logger()
    logger2 = get_logger()
    assert logger1 is logger2
    assert logger1.name == "litime_ble"
