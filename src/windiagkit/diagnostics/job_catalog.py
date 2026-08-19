from ..powershell.powershell_runner import PowerShellRunner
from ..powershell.script_loader import PowerShellScriptLoader
from ..validation import bounded_integer, network_target
from .command_spec import CommandSpec
from .events import LOGS
from .job_spec import JobSpec

_SCRIPT_LOADER = PowerShellScriptLoader()
_POWERSHELL_RUNNER = PowerShellRunner(script_loader=_SCRIPT_LOADER)

JOBS = (
    JobSpec(
        "checkpoint",
        "Load Test",
        "Complete diagnostic checkpoint",
        "Run resource, configuration, process, and focused event checks in sequence.",
        uses_event_window=True,
    ),
    JobSpec(
        "system_resources",
        "Load Test",
        "System resources and readiness",
        "Inspect CPU, memory, page file, uptime, and logical disk capacity.",
    ),
    JobSpec(
        "configuration_health",
        "Load Test",
        "Hardware and configuration health",
        "Inspect physical disks, restart indicators, power plan, devices, and services.",
    ),
    JobSpec(
        "process_snapshot",
        "Load Test",
        "Process resource snapshot",
        "Show configured targets and the busiest processes by memory, CPU time, and handles.",
    ),
    JobSpec(
        "load_test_events",
        "Event Logs",
        "Load-relevant warnings and errors",
        "Focus on crashes, resource exhaustion, hardware, storage, graphics, and networking.",
        uses_event_window=True,
    ),
    JobSpec(
        "system_events",
        "Event Logs",
        "System warnings and errors",
        "Show recent critical, error, and warning entries from the Windows System log.",
        uses_event_window=True,
    ),
    JobSpec(
        "dns_events",
        "Event Logs",
        "DNS Client operational log",
        "Inspect recent DNS Client operational events when that log is enabled.",
        uses_event_window=True,
    ),
    JobSpec(
        "network_events",
        "Event Logs",
        "Network Profile operational log",
        "Inspect network profile transitions and connectivity events.",
        uses_event_window=True,
    ),
    JobSpec(
        "wlan_events",
        "Event Logs",
        "WLAN AutoConfig operational log",
        "Inspect wireless connection, authentication, and roaming events.",
        uses_event_window=True,
    ),
    JobSpec(
        "ping",
        "Network",
        "IPv4 and IPv6 ping",
        "Test reachability and latency over both IP families.",
        needs_target=True,
    ),
    JobSpec(
        "traceroute",
        "Network",
        "IPv4 and IPv6 route trace",
        "Display the routed path to the target without DNS lookups per hop.",
        needs_target=True,
    ),
    JobSpec(
        "dns_lookup",
        "Network",
        "DNS A and AAAA lookup",
        "Resolve IPv4 and IPv6 records using the Windows resolver.",
        needs_target=True,
    ),
    JobSpec(
        "ipconfig",
        "Network",
        "IP configuration",
        "Display Windows adapter, address, DNS, DHCP, and gateway configuration.",
    ),
)

JOB_BY_KEY = {job.key: job for job in JOBS}


def _command(title, command, timeout, display=None):
    return CommandSpec(title, tuple(command), timeout, display or " ".join(command))


def _powershell(title, script_name, replacements, timeout):
    script = _SCRIPT_LOADER.load(script_name, replacements)
    return _command(
        title,
        _POWERSHELL_RUNNER.command(script),
        timeout,
        f"PowerShell · {script_name}",
    )


def _event_commands(job_key, minutes, settings):
    if job_key == "load_test_events":
        return (
            _powershell(
                "Load-relevant event triage",
                "load_test_events.ps1",
                {"MINUTES": minutes, "MAX_EVENTS": settings.max_events},
                settings.event_query_timeout_seconds,
            ),
        )
    if job_key == "system_events":
        return (
            _powershell(
                "System warnings and errors",
                "system_warnings_errors.ps1",
                {"MINUTES": minutes, "MAX_EVENTS": settings.max_events},
                settings.event_query_timeout_seconds,
            ),
        )

    log_name = {
        "dns_events": LOGS["dns"],
        "network_events": LOGS["network"],
        "wlan_events": LOGS["wlan"],
    }[job_key]
    return (
        _powershell(
            JOB_BY_KEY[job_key].title,
            "operational_log.ps1",
            {
                "LOG_NAME": _SCRIPT_LOADER.literal(log_name),
                "MINUTES": minutes,
                "MAX_EVENTS": settings.max_events,
            },
            settings.event_query_timeout_seconds,
        ),
    )


def _health_command(job_key, settings):
    details = {
        "system_resources": (
            "System resources and readiness",
            "system_resources.ps1",
            {},
        ),
        "configuration_health": (
            "Hardware and configuration health",
            "configuration_health.ps1",
            {},
        ),
        "process_snapshot": (
            "Process resource snapshot",
            "process_snapshot.ps1",
            {
                "PROCESS_NAMES": _SCRIPT_LOADER.array(
                    settings.diagnostic_process_names
                ),
                "TOP_COUNT": settings.top_process_count,
            },
        ),
    }
    title, script_name, replacements = details[job_key]
    return _powershell(
        title,
        script_name,
        replacements,
        settings.command_timeout_seconds,
    )


def _network_commands(job_key, target, settings):
    if job_key == "ping":
        arguments = (
            "-n",
            str(settings.ping_count),
            "-w",
            str(settings.ping_timeout_ms),
        )
        return tuple(
            _command(
                f"IPv{family} ping",
                ("ping", f"-{family}", *arguments, target),
                settings.command_timeout_seconds,
            )
            for family in (4, 6)
        )
    if job_key == "traceroute":
        arguments = (
            "-d",
            "-h",
            str(settings.traceroute_max_hops),
            "-w",
            str(settings.traceroute_timeout_ms),
        )
        return tuple(
            _command(
                f"IPv{family} route trace",
                ("tracert", f"-{family}", *arguments, target),
                settings.command_timeout_seconds,
            )
            for family in (4, 6)
        )
    return (
        _powershell(
            "DNS A and AAAA lookup",
            "dns_resolution.ps1",
            {"HOST_NAME": _SCRIPT_LOADER.literal(target)},
            settings.command_timeout_seconds,
        ),
    )


def _build_job_commands(job_key, settings, target=None, minutes=None):
    job = JOB_BY_KEY.get(job_key)
    if job is None:
        raise ValueError(f"Unknown diagnostic job: {job_key}")

    event_minutes = settings.event_window_minutes
    if job.uses_event_window:
        event_minutes = settings.event_window_minutes if minutes is None else minutes
        event_minutes = bounded_integer("minutes", event_minutes, 1, 1440)

    if job_key == "checkpoint":
        return (
            _health_command("system_resources", settings),
            _health_command("configuration_health", settings),
            _health_command("process_snapshot", settings),
            *_event_commands("load_test_events", event_minutes, settings),
        )
    if job_key in {"system_resources", "configuration_health", "process_snapshot"}:
        return (_health_command(job_key, settings),)
    if job_key.endswith("events"):
        return _event_commands(job_key, event_minutes, settings)
    if job_key == "ipconfig":
        return (
            _command(
                "IP configuration",
                ("ipconfig", "/all"),
                settings.command_timeout_seconds,
            ),
        )

    return _network_commands(job_key, network_target(target), settings)


class JobCatalog:
    def __init__(self):
        self._jobs_by_key = JOB_BY_KEY

    @property
    def jobs(self):
        return JOBS

    def get(self, key):
        return self._jobs_by_key.get(key)

    def build_commands(self, key, settings, target=None, minutes=None):
        return _build_job_commands(key, settings, target=target, minutes=minutes)
