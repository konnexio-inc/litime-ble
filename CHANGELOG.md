# Changelog

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
