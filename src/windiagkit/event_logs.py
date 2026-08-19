from os import name

from .console_utils import run_visible
from .powershell_scripts import load_script


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


def _load_script(script_name, replacements):
    try:
        return load_script(script_name, replacements)
    except RuntimeError as exc:
        print(exc)
        return None


def show_operational_log(log_name, minutes=15, max_events=100, timeout=30.0):
    # The log may exist but be disabled. We report that without changing its state.
    minutes = _bounded_integer("minutes", minutes, 1, 1440)
    max_events = _bounded_integer("max_events", max_events, 1, 1000)
    log_literal = _powershell_literal(log_name)
    script = _load_script(
        "operational_log.ps1",
        {"LOG_NAME": log_literal, "MINUTES": minutes, "MAX_EVENTS": max_events},
    )
    if script is None:
        return False
    return _powershell(script, timeout)


def show_system_warnings_errors(minutes=15, max_events=100, timeout=30.0):
    minutes = _bounded_integer("minutes", minutes, 1, 1440)
    max_events = _bounded_integer("max_events", max_events, 1, 1000)
    script = _load_script(
        "system_warnings_errors.ps1",
        {"MINUTES": minutes, "MAX_EVENTS": max_events},
    )
    if script is None:
        return False
    return _powershell(script, timeout)


def show_dns_log(minutes=15, max_events=100, timeout=30.0):
    return show_operational_log(LOGS["dns"], minutes, max_events, timeout)


def show_network_profile_log(minutes=15, max_events=100, timeout=30.0):
    return show_operational_log(LOGS["network"], minutes, max_events, timeout)


def show_wlan_log(minutes=15, max_events=100, timeout=30.0):
    return show_operational_log(LOGS["wlan"], minutes, max_events, timeout)
