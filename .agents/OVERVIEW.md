# Agent Overview

Read `.agents/PROJECT_CACHE.md` first. Then open only the guide relevant to the
task:

- debugging or regression work: `.agents/debugging/README.md`
- review, refactoring, or release checks: `.agents/quality/README.md`
- architecture context: `docs/ARCHITECTURE.md`
- setup and builds: `docs/DEVELOPMENT.md`
- diagnostic and security scope: `docs/DIAGNOSTICS.md`

Avoid re-reading the full repository unless the cache is stale. Use `rg` and
targeted tests first; run the complete suite before handing off code changes.
