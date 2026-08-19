# Development and Builds

## Virtual environment

```bat
py -3.14-64 -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

Run `windiagkit-gui` for the GUI or `windiagkit` for the console.

## Validation

```bat
ruff check src tests
ruff format --check src tests
python -m unittest discover -v
python src\gui_main.py --smoke-test
```

## Executables

- x64: activate a 64-bit environment and run `scripts\build_x64.bat`.
- x86: activate a 32-bit environment and run `scripts\build_x86.bat`.

PyInstaller follows the architecture of its Python interpreter and does not
cross-compile. Normal dependencies and tooling live in `pyproject.toml`; only
the win32 wheel constraints remain in `requirements-x86.txt`.
