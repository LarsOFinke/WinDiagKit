# Architecture

WinDiagKit uses a `src` package layout and small responsibility-oriented
modules. Each production class has its own file.

```text
entrypoint -> configuration -> UI/console -> diagnostic job
                                      |-> PowerShell runner -> bundled script
                                      |-> native Windows command
```

Core responsibilities:

- `settings.py`: immutable validated application values.
- `configuration_loader.py` and `config.py`: configuration boundary and parsing.
- `diagnostics/job_catalog.py`: job metadata and bounded command construction.
- `powershell/script_loader.py`: safe bundled-template loading and literal escaping.
- `powershell/powershell_runner.py`: Windows-only execution policy.
- `gui/job_runner.py`: asynchronous sequential processes, cancellation, and timeouts.
- `gui/main_window.py`: presentation and user interaction orchestration.

Qt-independent diagnostics do not import the GUI. Operating-system and process
boundaries are isolated so tests can replace them without executing diagnostics.
