from ..powershell.powershell_runner import PowerShellRunner
from ..validation import bounded_integer

DIAGNOSTIC_NOTICE = "Read-only diagnostic. Results are displayed only."
_POWERSHELL_RUNNER = PowerShellRunner()


def show_system_resources(timeout=30.0):
    return _POWERSHELL_RUNNER.run(
        "system_resources.ps1", {}, timeout, DIAGNOSTIC_NOTICE
    )


def show_configuration_health(timeout=30.0):
    return _POWERSHELL_RUNNER.run(
        "configuration_health.ps1", {}, timeout, DIAGNOSTIC_NOTICE
    )


def show_load_test_events(minutes=15, max_events=100, timeout=30.0):
    minutes = bounded_integer("minutes", minutes, 1, 10080)
    max_events = bounded_integer("max_events", max_events, 1, 1000)
    return _POWERSHELL_RUNNER.run(
        "load_test_events.ps1",
        {"Minutes": minutes, "MaxEvents": max_events},
        timeout,
        DIAGNOSTIC_NOTICE,
    )


def show_process_snapshot(process_names=(), top_count=15, timeout=30.0):
    top_count = bounded_integer("top_count", top_count, 5, 50)
    return _POWERSHELL_RUNNER.run(
        "process_snapshot.ps1",
        {
            "ProcessNamesCsv": ",".join(process_names),
            "TopCount": top_count,
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
