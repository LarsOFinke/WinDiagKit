# Project Cache

- Product: read-only Windows diagnostics GUI and console toolkit.
- Python: 3.10-3.14; normal build is x64, exceptional x86 pins are in
  `requirements-x86.txt`.
- Packaging: `pyproject.toml`; source layout under `src/windiagkit`.
- Entrypoints: `windiagkit`, `windiagkit-gui`, `python -m windiagkit`, and
  `src/gui_main.py` for PyInstaller.
- UI: PyQt5; asynchronous commands use `gui/job_runner.py`.
- Job construction: `diagnostics/job_catalog.py`.
- PowerShell boundary: `powershell/powershell_runner.py`; safe template loading:
  `powershell/script_loader.py`.
- Bundled scripts: `powershell/scripts/*.ps1`; all are intended to be read-only.
- Configuration: immutable `Settings` plus `ConfigurationLoader`.
- Tests: standard-library `unittest`; Windows processes are mocked.

Fast validation:

```bash
ruff check src tests
ruff format --check src tests
PYTHONPATH=src QT_QPA_PLATFORM=offscreen python -m unittest discover -v
```

Update this cache only when architecture, commands, dependencies, or supported
platforms change.
