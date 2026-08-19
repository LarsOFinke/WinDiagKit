from os import name

from .console_utils import run_visible


LOGS = {
    "dns": "Microsoft-Windows-DNS-Client/Operational",
    "network": "Microsoft-Windows-NetworkProfile/Operational",
    "wlan": "Microsoft-Windows-WLAN-AutoConfig/Operational",
}


def _powershell(script, timeout=30.0):
    if name != "nt":
        print("This function is intended for Windows.")
        return False

    print("\nRead-only Event Viewer query. Nothing is exported or saved.\n")
    return run_visible(
        [
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ],
        timeout=timeout,
    )


def _bounded_integer(name, value, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _powershell_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def show_operational_log(log_name, minutes=15, max_events=100, timeout=30.0):
    # The log may exist but be disabled. We report that without changing its state.
    minutes = _bounded_integer("minutes", minutes, 1, 1440)
    max_events = _bounded_integer("max_events", max_events, 1, 1000)
    log_literal = _powershell_literal(log_name)
    script = rf'''
$logName = {log_literal}
try {{
    $log = Get-WinEvent -ListLog $logName -ErrorAction Stop
}} catch {{
    Write-Host "Could not inspect log: $($_.Exception.Message)"
    exit 1
}}
if (-not $log) {{
    Write-Host "Log not available: $logName"
    exit
}}

Write-Host "Log: $logName"
Write-Host "Enabled: $($log.IsEnabled)"
Write-Host "Window: last {minutes} minute(s)"
Write-Host ""

if (-not $log.IsEnabled) {{
    Write-Host "This Operational log is currently disabled."
    Write-Host "WinDiagKit will not enable it automatically because that changes system state."
    exit
}}

$start = (Get-Date).AddMinutes(-{minutes})
try {{
    $events = @(Get-WinEvent -FilterHashtable @{{
        LogName = $logName
        StartTime = $start
    }} -ErrorAction Stop |
    Select-Object -First {max_events} TimeCreated, Id, LevelDisplayName, ProviderName, Message)
}} catch {{
    if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') {{
        Write-Host "No matching events found."
        exit
    }}
    Write-Host "Event query failed: $($_.Exception.Message)"
    exit 1
}}

if ($events.Count -eq 0) {{
    Write-Host "No matching events found."
}} else {{
    $events | Format-List
}}
'''
    return _powershell(script, timeout)


def show_system_warnings_errors(minutes=15, max_events=100, timeout=30.0):
    minutes = _bounded_integer("minutes", minutes, 1, 1440)
    max_events = _bounded_integer("max_events", max_events, 1, 1000)
    script = rf'''
$start = (Get-Date).AddMinutes(-{minutes})
Write-Host "System log - Critical / Error / Warning"
Write-Host "Window: last {minutes} minute(s)"
Write-Host ""

try {{
    $events = @(Get-WinEvent -FilterHashtable @{{
        LogName = 'System'
        StartTime = $start
        Level = 1,2,3
    }} -ErrorAction Stop |
    Select-Object -First {max_events} TimeCreated, Id, LevelDisplayName, ProviderName, Message)
}} catch {{
    if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') {{
        Write-Host "No matching events found."
        exit
    }}
    Write-Host "Event query failed: $($_.Exception.Message)"
    exit 1
}}

if ($events.Count -eq 0) {{
    Write-Host "No matching events found."
}} else {{
    $events | Format-List
}}
'''
    return _powershell(script, timeout)


def show_dns_log(minutes=15, max_events=100, timeout=30.0):
    return show_operational_log(LOGS["dns"], minutes, max_events, timeout)


def show_network_profile_log(minutes=15, max_events=100, timeout=30.0):
    return show_operational_log(LOGS["network"], minutes, max_events, timeout)


def show_wlan_log(minutes=15, max_events=100, timeout=30.0):
    return show_operational_log(LOGS["wlan"], minutes, max_events, timeout)
