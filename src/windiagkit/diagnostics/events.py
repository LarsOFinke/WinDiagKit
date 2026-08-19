from ..powershell.powershell_runner import PowerShellRunner
from ..validation import bounded_integer

LOGS = {
    "dns": "Microsoft-Windows-DNS-Client/Operational",
    "network": "Microsoft-Windows-NetworkProfile/Operational",
    "wlan": "Microsoft-Windows-WLAN-AutoConfig/Operational",
}


EVENT_NOTICE = "Read-only Event Viewer query. Nothing is exported or saved."
_POWERSHELL_RUNNER = PowerShellRunner()


def show_operational_log(log_name, minutes=15, max_events=100, timeout=30.0):
    # The log may exist but be disabled. We report that without changing its state.
    minutes = bounded_integer("minutes", minutes, 1, 1440)
    max_events = bounded_integer("max_events", max_events, 1, 1000)
    return _POWERSHELL_RUNNER.run(
        "operational_log.ps1",
        {
            "LOG_NAME": _POWERSHELL_RUNNER.script_loader.literal(log_name),
            "MINUTES": minutes,
            "MAX_EVENTS": max_events,
        },
        timeout,
        EVENT_NOTICE,
    )


def show_system_warnings_errors(minutes=15, max_events=100, timeout=30.0):
    minutes = bounded_integer("minutes", minutes, 1, 1440)
    max_events = bounded_integer("max_events", max_events, 1, 1000)
    return _POWERSHELL_RUNNER.run(
        "system_warnings_errors.ps1",
        {"MINUTES": minutes, "MAX_EVENTS": max_events},
        timeout,
        EVENT_NOTICE,
    )


def show_dns_log(minutes=15, max_events=100, timeout=30.0):
    return show_operational_log(LOGS["dns"], minutes, max_events, timeout)


def show_network_profile_log(minutes=15, max_events=100, timeout=30.0):
    return show_operational_log(LOGS["network"], minutes, max_events, timeout)


def show_wlan_log(minutes=15, max_events=100, timeout=30.0):
    return show_operational_log(LOGS["wlan"], minutes, max_events, timeout)
