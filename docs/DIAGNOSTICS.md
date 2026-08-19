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

One-file PyInstaller executables extract native runtime files temporarily,
which can attract heuristic antivirus scrutiny. Keep UPX disabled, provide a
source commit and SHA-256 hash, sign releases when possible, and submit suspected
false positives to the antivirus vendor. Never instruct users to disable their
protection.
