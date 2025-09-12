---
title: Developer
---

## Tests

Run tests locally:

PowerShell:

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
python -m pytest -q
```

macOS / Linux

```bash
PYTHONPATH=$(pwd)/src python -m pytest -q
```

## Linting

```bash
ruff check src --fix
ruff check src
```

## GitHub Actions

This repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs ruff and pytest on Python 3.10, 3.11 and 3.12.

To publish docs to GitHub Pages, a second workflow (`.github/workflows/deploy-pages.yml`) is provided to build and push the contents of the `docs/` folder to the Pages branch.
