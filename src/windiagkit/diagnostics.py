from .powershell_runner import run_powershell
from .powershell_scripts import powershell_array
from .validation import bounded_integer

DIAGNOSTIC_NOTICE = "Read-only diagnostic. Results are displayed only."


def show_system_resources(timeout=30.0):
    return run_powershell("system_resources.ps1", {}, timeout, DIAGNOSTIC_NOTICE)


def show_configuration_health(timeout=30.0):
    return run_powershell("configuration_health.ps1", {}, timeout, DIAGNOSTIC_NOTICE)


def show_load_test_events(minutes=15, max_events=100, timeout=30.0):
    minutes = bounded_integer("minutes", minutes, 1, 1440)
    max_events = bounded_integer("max_events", max_events, 1, 1000)
    return run_powershell(
        "load_test_events.ps1",
        {"MINUTES": minutes, "MAX_EVENTS": max_events},
        timeout,
        DIAGNOSTIC_NOTICE,
    )


def show_process_snapshot(process_names=(), top_count=15, timeout=30.0):
    top_count = bounded_integer("top_count", top_count, 5, 50)
    return run_powershell(
        "process_snapshot.ps1",
        {
            "PROCESS_NAMES": powershell_array(process_names),
            "TOP_COUNT": top_count,
        },
        timeout,
        DIAGNOSTIC_NOTICE,
    )


def show_load_test_checkpoint(settings):
    checks = (
        show_system_resources(settings.command_timeout_seconds),
        show_configuration_health(settings.command_timeout_seconds),
        show_process_snapshot(
            settings.diagnostic_process_names,
            settings.top_process_count,
            settings.command_timeout_seconds,
        ),
        show_load_test_events(
            settings.event_window_minutes,
            settings.max_events,
            settings.event_query_timeout_seconds,
        ),
    )
    return all(checks)
