# WinDiagKit

Small read-only Windows troubleshooting console for live system metrics, IPv4/IPv6 checks, and selected Event Viewer logs.

## Run from Python

```bat
python -m pip install -r requirements.txt
python main.py
```

## Build x86 EXE

Run `build_x86.bat` from a **32-bit Python** environment.

## Project layout

- `main.py` - entry point only
- `menus.py` - interactive console navigation
- `system_monitor.py` - CPU/RAM/network/GPU/temperature monitor
- `network_tools.py` - `ipconfig`, DNS, ping, traceroute
- `event_logs.py` - read-only Event Viewer queries
- `console_utils.py` - shared console/subprocess helpers

## Privacy / state changes

WinDiagKit does not intentionally save collected diagnostic output to files. Event logs are queried read-only. Operational logs that are disabled are reported as disabled and are **not enabled automatically**.

`ipconfig /all` and Event Viewer output can still contain sensitive information when copied or screenshotted.
