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

Both scripts produce a non-self-extracting directory build at
`dist\WinDiagKit`. Distribute the whole directory. UPX remains disabled and
standard Windows properties come from `scripts\windows_version_info.txt`.
The application honors the target system's PowerShell execution policy; it does
not bypass a policy that prevents script execution.

For signed releases, install the code-signing certificate in the Windows
certificate store and set `WINDIAGKIT_SIGN_CERT_SHA1` to its thumbprint before
running the build. The script requires `signtool.exe`, applies an SHA-256
Authenticode signature, timestamps it, and fails if signing does not succeed.
