# Changelog

## [Unreleased]

### Fixed

- **`sync()` reads failing with "attached to a different loop"** ([#2](https://github.com/konnexio-inc/litime-ble/issues/2))
  - `read_once()` inside `with client.sync()` now runs on the event loop that opened the connection, instead of a new one
  - `sync()` keeps one background event loop running for the whole block, so repeated reads reuse the connection
  - `sync()` now uses the client's own settings (e.g. `request_timeout_s`) instead of a copy with defaults
  - `read_once()` on a connected client raises a clear `RuntimeError` instead of hanging or failing mid-exchange when called from the connection's own loop, or after that loop has stopped
- **Docs**: the `sync()` example called it as `BatteryClient.sync(address=...)`, which raises `TypeError`; it is now `BatteryClient(address=...).sync()`

## [0.2.2] - 2025-09-12

### Fixed

- **ROS2 Event Loop Compatibility**: Completely resolved event loop conflicts in ROS2 environments
  - Improved threaded execution approach for sync operations
  - Smart detection of connected state to maintain test compatibility
  - Fixed CLI to use simplified read approach avoiding double connection attempts
  - All operations now properly isolated to prevent D-Bus/event loop interference

### Enhanced

- **Robust Execution Strategy**: Always uses threaded approach for new connections to ensure compatibility across all environments
- **Test Compatibility**: Maintains backward compatibility with existing test suite and mock objects

## [0.2.1] - 2025-09-12

### Fixed

- **Event Loop Compatibility**: Fixed CLI compatibility with environments that have existing event loops (e.g., ROS2)
  - Automatic detection of running event loops
  - Threaded execution approach when event loop conflicts are detected
  - Maintains full functionality in both standalone and framework environments
- **Deprecated API Warning**: Replaced deprecated `get_services()` call with `services` property
  - Eliminates FutureWarning from Bleak library

### Enhanced

- **Debug Logging**: Added event loop detection logging for troubleshooting
  - Shows which execution approach is being used (direct vs threaded)

## [0.2.0] - 2025-09-12

### Added

- **Device Discovery**: New BLE device discovery functionality
  - `discover_devices()` and `discover_devices_sync()` for general BLE scanning
  - `find_litime_batteries()` and `find_litime_batteries_sync()` for Li-Time specific discovery
  - `format_device_info()` helper for displaying device information
- **Enhanced Logging**: Configurable logging system with multiple levels
  - `configure_logging()` function with DEBUG, INFO, WARNING, ERROR levels
  - Better diagnostic output for troubleshooting connection issues
- **CLI Module Support**: Package can now be run as `python -m litime_ble`
- **Comprehensive Examples**: Full examples directory with standardized CLI tools
  - `battery_read_sync.py` - Simple synchronous battery reading
  - `battery_read_async.py` - Async reading with retries and detailed output
  - `device_discovery.py` - Interactive and non-interactive device discovery
  - `debug_test.py` - Quick debugging tool
  - `logging_test.py` - Logging demonstration and diagnostics
- **Package Version**: Added `__version__` attribute accessible via `import litime_ble; litime_ble.__version__`

### Enhanced

- **Improved Battery Detection**: Better pattern matching for Li-Time device names
- **Test Coverage**: Expanded test suite covering discovery and logging functionality
- **Documentation**: Enhanced examples with consistent CLI patterns and usage docs
- **Error Handling**: More robust connection and protocol error handling

### Fixed

- **License Format**: Updated to modern SPDX format in package metadata
- **Package Building**: Resolved deprecation warnings in build process
- **Import Structure**: Cleaner module organization and exports

### Technical Details

- Enhanced BLE discovery with RSSI signal strength reporting
- Support for both interactive and non-interactive usage patterns
- Consistent argparse CLI across all example scripts
- Professional logging configuration with conditional debug output
- Improved packaging with MANIFEST.in for proper file inclusion

## [0.1.8] - Previous Release

- Initial stable release with basic battery reading functionality
