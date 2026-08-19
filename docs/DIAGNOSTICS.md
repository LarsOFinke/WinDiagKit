# Diagnostic and Security Scope

WinDiagKit collects live resource metrics, selected Windows Event Viewer data,
network configuration/connectivity results, hardware/configuration health, and
focused process snapshots for before/after load-test comparison.

The project does not intentionally modify services, registry values, power
plans, logs, Defender settings, startup state, or user files. It does not add
persistence, download payloads, execute encoded commands, or disable security
software. Output remains in memory unless the user explicitly copies it.

Network jobs create ordinary DNS, ICMP, and traceroute traffic. Event and
configuration output may contain sensitive host names, addresses, account data,
or device details. Treat copied output and screenshots accordingly.

For Event Viewer jobs, the GUI provides fixed lookback choices for the last 15
minutes, hour, day, and week. The selected value is passed only to that run and
does not require an INI change.

PowerShell diagnostics execute the visible bundled `.ps1` resources with
`-File`; inputs are separate arguments. WinDiagKit does not use inline or encoded
commands and does not bypass Windows execution policy.

Release builds use PyInstaller directory mode so they do not self-extract at
runtime. UPX is disabled, Windows version metadata is included, and the build
can Authenticode-sign when a certificate thumbprint is supplied. These choices
reduce avoidable heuristic signals but cannot guarantee that every scanner will
classify every new unsigned binary correctly. Provide a source commit and
SHA-256 hash, submit suspected false positives to the vendor, and never instruct
users to disable their protection.
