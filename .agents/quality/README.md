# Quality Guide

Preserve these invariants:

- diagnostics are read-only and do not weaken antivirus or system security;
- subprocesses use argument lists, bounded timeouts, and no shell interpolation;
- PowerShell uses bundled files with `-File`, never inline/encoded commands or
  execution-policy bypasses;
- each production class has one module and one clear responsibility;
- inject process/script collaborators where behavior needs isolation;
- keep stateless validation and formatting as functions;
- avoid compatibility wrappers unless a supported public API requires one;
- package every PowerShell resource and keep x86-specific pins isolated.
- keep release builds in `--onedir` mode with UPX disabled and metadata current.

Before handoff, run lint, formatting, compilation, all tests, source GUI smoke,
and a clean PyInstaller smoke test when packaging paths changed. Check
`git diff --check` and document any platform limitation explicitly.
