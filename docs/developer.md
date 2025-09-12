---
title: "Developer"
layout: single
permalink: /developer/
---

## Development Setup

Install in editable mode for development:

```bash
pip install -e .
pip install pytest pytest-asyncio ruff
```

## Tests

Run the full test suite:

**PowerShell:**

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
python -m pytest -v
```

**macOS / Linux:**

```bash
PYTHONPATH=$(pwd)/src python -m pytest -v
```

Current test coverage: 21 tests covering client operations, discovery, logging, and protocol parsing.

## Linting

Code quality with ruff:

```bash
ruff check src --fix   # Auto-fix issues
ruff check src         # Check only
```

## Examples

The `examples/` directory contains comprehensive example scripts:

- `device_discovery.py` - BLE device discovery with various options
- `battery_read_sync.py` - Simple synchronous battery reading
- `battery_read_async.py` - Async reading with retries
- `debug_test.py` - Quick debugging tool
- `logging_test.py` - Logging system demonstration

All examples support `--help` and consistent CLI patterns.

## Building

Build distributions:

```bash
pip install build
python -m build --sdist --wheel
```

## GitHub Actions

### CI Workflow (`.github/workflows/ci.yml`)

Runs on push/PR to main:

- Tests on Python 3.10, 3.11, 3.12
- Ruff linting
- Package installation verification

### PyPI Publishing (`.github/workflows/publish-pypi.yml`)

Triggered by version tags (`v*`):

- Builds source and wheel distributions
- Publishes to TestPyPI and PyPI via Trusted Publisher

### Documentation (`.github/workflows/deploy-pages.yml`)

Builds and deploys Jekyll docs to GitHub Pages from the `docs/` folder.

## Release Process

1. Update version in `pyproject.toml` and `src/litime_ble/__init__.py`
2. Update `CHANGELOG.md` with release notes
3. Commit changes: `git commit -m "Release X.Y.Z"`
4. Tag release: `git tag vX.Y.Z`
5. Push with tags: `git push origin main --tags`

The GitHub Actions workflow automatically handles PyPI publishing.
