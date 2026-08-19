import os
import subprocess


LOGS = {
    "dns": "Microsoft-Windows-DNS-Client/Operational",
    "network": "Microsoft-Windows-NetworkProfile/Operational",
    "wlan": "Microsoft-Windows-WLAN-AutoConfig/Operational",
}


def _powershell(script):
    if os.name != "nt":
        print("This function is intended for Windows.")
        return

    print("\nRead-only Event Viewer query. Nothing is exported or saved.\n")
    subprocess.run(
        [
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ],
        check=False,
    )


def show_operational_log(log_name, minutes=15, max_events=100):
    # The log may exist but be disabled. We report that without changing its state.
    script = rf'''
$logName = '{log_name}'
$log = Get-WinEvent -ListLog $logName -ErrorAction SilentlyContinue
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
Get-WinEvent -FilterHashtable @{{
    LogName = $logName
    StartTime = $start
}} -ErrorAction SilentlyContinue |
Select-Object -First {max_events} TimeCreated, Id, LevelDisplayName, ProviderName, Message |
Format-List
'''
    _powershell(script)


def show_system_warnings_errors(minutes=15, max_events=100):
    script = rf'''
$start = (Get-Date).AddMinutes(-{minutes})
Write-Host "System log - Critical / Error / Warning"
Write-Host "Window: last {minutes} minute(s)"
Write-Host ""

Get-WinEvent -FilterHashtable @{{
    LogName = 'System'
    StartTime = $start
    Level = 1,2,3
}} -ErrorAction SilentlyContinue |
Select-Object -First {max_events} TimeCreated, Id, LevelDisplayName, ProviderName, Message |
Format-List
'''
    _powershell(script)


def show_dns_log(minutes=15):
    show_operational_log(LOGS["dns"], minutes)


def show_network_profile_log(minutes=15):
    show_operational_log(LOGS["network"], minutes)


def show_wlan_log(minutes=15):
    show_operational_log(LOGS["wlan"], minutes)
