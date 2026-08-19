# WinDiagKit

WinDiagKit is a small, read-only Windows troubleshooting console for live system
metrics, IPv4/IPv6 checks, and selected Event Viewer logs.

Current version: **0.3.0**

## Supported environment

- Windows 10 or 11, x86 or x64
- CPython 3.10 through 3.14
- NVIDIA GPU metrics require `nvidia-smi`; all other features continue without it

The live monitor and DNS resolver can partly operate on other platforms, but the
application's supported target is Windows.

## Run from Python

```bat
python -m pip install -r requirements.txt
python src\main.py
```

## Configuration

Configuration is optional. Without a configuration file, WinDiagKit uses safe
built-in defaults. To customize it, copy `winddiagkit.ini.example` to
`winddiagkit.ini` in the project root or beside the built EXE, edit it, and
restart the app.

You can select a file elsewhere by setting `WINDIAGKIT_CONFIG`:

```bat
set WINDIAGKIT_CONFIG=C:\Tools\WinDiagKit\office.ini
python src\main.py
```

Available settings include:

- default network target, ping count, and ping timeout
- traceroute hop limit and per-hop timeout
- overall network command timeout
- Event Viewer time-window choices, maximum results, and query timeout
- monitor sampling, ACPI refresh, and helper-command intervals
- process names and process-table size for load-test diagnostic snapshots

Invalid values are reported at startup and replaced with built-in defaults.
The complete documented template is in `winddiagkit.ini.example`.

## Build x86 EXE

Run `scripts\build_x86.bat` with a 32-bit Python environment on `PATH`. The
script resolves the project root automatically, rejects a 64-bit interpreter,
installs the pinned x86-compatible build dependencies, disables optional UPX
compression, and creates `dist\WinDiagKit.exe`. The x86 build uses psutil 6.1.1,
the latest release that provides a compatible Windows win32 wheel; normal source
installations use the current version pinned in `requirements.txt`.

To customize the built application, copy `winddiagkit.ini.example` to
`dist\winddiagkit.ini`.

## Tests

The tests use only Python's standard library test runner:

```bat
python -m unittest discover -v
```

Windows commands are mocked in unit tests so the suite is safe to run on other
platforms. A real Windows smoke test is still recommended for release builds.

## Load-test diagnostics

The **Load-test diagnostics** menu provides a read-only checkpoint before or
after reproducing a problem. Resource readiness and hardware/configuration
health are separate checks, so each can be run independently. Together they
cover memory and page-file state, disk capacity and health, pending restart
indicators, the active power plan, device errors, and automatic services.
Event triage focuses on application crashes/hangs, resource exhaustion,
hardware, storage, graphics, power, service, and core network providers.

For easier identification of affected programs, set `process_names` in the
`[diagnostics]` section of `winddiagkit.ini`. Use comma-separated executable
names with or without `.exe`; do not enter paths. A complete checkpoint displays
all results in the console and does not modify services, power settings, logs,
registry values, or files.

Useful sequence for a load test:

1. Run a complete diagnostic checkpoint immediately before the test.
2. Run the live system monitor during the test.
3. Run another complete checkpoint directly after the issue occurs.
4. Compare timestamps, warnings, event IDs, and target-process resource values.

## Project layout

- `src/main.py` - direct source and PyInstaller entry point
- `src/windiagkit/` - application package and diagnostic modules
- `src/windiagkit/powershell/` - focused read-only PowerShell diagnostics
- `src/windiagkit/diagnostics.py` - load-test diagnostic orchestration
- `src/windiagkit/powershell_runner.py` - shared PowerShell execution boundary
- `scripts/` - Windows build and maintenance scripts
- `tests/` - automated unit tests

## Privacy and state changes

WinDiagKit does not intentionally save collected diagnostic output to files.
Event logs are queried read-only. Operational logs that are disabled are
reported as disabled and are not enabled automatically.

Network tests generate normal DNS, ICMP, and traceroute traffic. `ipconfig /all`
and Event Viewer output can contain sensitive information when copied or
screenshotted.

PyInstaller's `--onefile` mode extracts its runtime to a temporary directory;
WinDiagKit itself does not export or persist collected diagnostic data.

## Security and antivirus review

WinDiagKit has no persistence, installer, service, registry, privilege-
escalation, download, obfuscated-payload, or self-modifying behavior. Its
diagnostic actions are visible and intentional: it may invoke Windows
`ipconfig`, `ping`, `tracert`, PowerShell `Get-WinEvent`/CIM queries, and an
installed `nvidia-smi` executable. User targets are passed as argument-list
elements, not interpolated into a shell command.

No software can guarantee that every antivirus engine will accept an unsigned
PyInstaller executable. One-file PyInstaller bundles unpack native support
files into a temporary `_MEI...` directory at launch, which is a known source
of heuristic scrutiny. The build disables UPX compression to avoid an
additional packer signal. For target-system analysis, provide the SHA-256 hash
printed by the build script, the source commit, and the EXE from a clean build
machine. If enterprise policy permits, Authenticode-sign the EXE; never ask a
recipient to disable antivirus protection. Submit any suspected false positive
to the relevant vendor for analysis.

## License

WinDiagKit is available under the MIT License. See `LICENSE`.
