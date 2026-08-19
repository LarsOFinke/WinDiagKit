# Changelog

## 0.2.0 - 2026-08-19

- Add validated INI configuration for network, event log, and monitor settings.
- Bound ping, traceroute, Event Viewer, and helper command execution times.
- Report missing commands, timeouts, and nonzero command exits.
- Distinguish empty Event Viewer results from query failures.
- Add automated unit tests for configuration and diagnostic helpers.
- Pin runtime and build dependencies for reproducible builds.
- Add an x86 interpreter check to the Windows build script.
- Adopt a `src/windiagkit` package layout and a dedicated `scripts` directory.

## 0.1.0

- Initial prototype with system, network, and Event Viewer diagnostics.
