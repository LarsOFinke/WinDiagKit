# Changelog

## 0.4.0 - 2026-08-19

- Add a PyQt5 desktop interface with live system metrics and categorized jobs.
- Stream diagnostic output without blocking the UI and support safe cancellation.
- Add searchable, color-highlighted in-memory logs and contextual job controls.
- Build the x86 executable as a windowed GUI while retaining the console entry.
- Group CLI, diagnostics, GUI, and PowerShell code into focused subpackages and
  mirror that structure in the test suite.
- Give every production class its own module and introduce focused configuration,
  PowerShell, and job-catalog service objects.
- Add a dedicated x64 PyInstaller build script and architecture-specific build
  dependency files while retaining the x86 build.
- Add `pyproject.toml` packaging metadata, virtual-environment installation,
  console/GUI commands, development extras, and bundled script resources.
- Consolidate dependency files, remove legacy compatibility facades, and add
  human and token-conscious agent documentation.
- Relax the normal Qt runtime pin to a compatible 5.15 range so pip can resolve
  the wheel available for the active Python/platform.

## 0.3.0 - 2026-08-19

- Add read-only system-readiness, focused event-triage, and process-snapshot
  diagnostics for before/after load-test checkpoints.
- Add configurable target-process names and snapshot table size.
- Split resource and configuration checks into focused scripts and centralize
  validated PowerShell execution.

## 0.2.0 - 2026-08-19

- Add validated INI configuration for network, event log, and monitor settings.
- Bound ping, traceroute, Event Viewer, and helper command execution times.
- Report missing commands, timeouts, and nonzero command exits.
- Distinguish empty Event Viewer results from query failures.
- Add automated unit tests for configuration and diagnostic helpers.
- Pin runtime and build dependencies for reproducible builds.
- Add an x86 interpreter check to the Windows build script.
- Adopt a `src/windiagkit` package layout and a dedicated `scripts` directory.
- Move Event Viewer PowerShell into bundled project templates.
- Use the latest psutil release with a win32 wheel for reproducible x86 builds.
- Cover Windows ACPI and monitor execution paths with regression tests.

## 0.1.0

- Initial prototype with system, network, and Event Viewer diagnostics.
