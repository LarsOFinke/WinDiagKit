# Debugging Guide

1. Reproduce with the narrowest affected test module.
2. Trace imports and call sites with `rg`; inspect only the relevant package.
3. Patch OS/process boundaries in tests—never invoke Windows diagnostics during
   cross-platform unit tests.
4. For GUI failures, set `QT_QPA_PLATFORM=offscreen` and process Qt events.
5. For packaged failures, verify both the frozen smoke test and that every
   `powershell/scripts/*.ps1` resource exists in the archive.

Common boundaries:

- command lifecycle/timeouts: `gui/job_runner.py`
- command creation: `diagnostics/job_catalog.py`
- PowerShell loading/execution: `powershell/`
- settings fallback behavior: `config.py` and `configuration_loader.py`
