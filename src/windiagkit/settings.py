"""Immutable application settings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    default_target: str = "example.com"
    event_window_minutes: int = 15
    event_window_choices: tuple = (5, 15, 30, 60)
    max_events: int = 100
    event_query_timeout_seconds: float = 30.0
    ping_count: int = 4
    ping_timeout_ms: int = 2000
    traceroute_max_hops: int = 20
    traceroute_timeout_ms: int = 1000
    command_timeout_seconds: float = 30.0
    sample_seconds: float = 1.0
    acpi_refresh_seconds: float = 5.0
    helper_timeout_seconds: float = 4.0
    diagnostic_process_names: tuple = ()
    top_process_count: int = 15
