import sys
from configparser import ConfigParser, Error
from dataclasses import dataclass
from os import environ
from pathlib import Path

CONFIG_ENV_VAR = "WINDIAGKIT_CONFIG"


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


def default_config_path():
    override = environ.get(CONFIG_ENV_VAR)
    if override:
        return Path(override).expanduser()
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().with_name("winddiagkit.ini")
    return Path(__file__).resolve().parents[2] / "winddiagkit.ini"


def _read_value(
    parser, section, option, default, converter, minimum, maximum, warnings
):
    if not parser.has_option(section, option):
        return default
    try:
        value = converter(parser.get(section, option))
        if not minimum <= value <= maximum:
            raise ValueError
        return value
    except (Error, ValueError):
        warnings.append(
            f"[{section}] {option} must be between {minimum} and {maximum}; "
            f"using {default}."
        )
        return default


def _read_choices(parser, default, warnings):
    if not parser.has_option("events", "window_choices"):
        return default
    try:
        values = tuple(
            int(item.strip())
            for item in parser.get("events", "window_choices").split(",")
            if item.strip()
        )
        if not values or len(set(values)) != len(values):
            raise ValueError
        if any(value < 1 or value > 1440 for value in values):
            raise ValueError
        return values
    except (Error, ValueError):
        warnings.append(
            "[events] window_choices must be unique comma-separated minutes from 1 to "
            f"1440; using {','.join(map(str, default))}."
        )
        return default


def _read_target(parser, default, warnings):
    target = parser.get("network", "default_target", fallback=default).strip()
    if target and len(target) <= 253 and not any(char.isspace() for char in target):
        return target
    warnings.append(f"[network] default_target is invalid; using {default}.")
    return default


def _read_section_values(parser, section, defaults, specifications, warnings):
    return {
        field: _read_value(
            parser,
            section,
            option,
            getattr(defaults, field),
            converter,
            minimum,
            maximum,
            warnings,
        )
        for field, option, converter, minimum, maximum in specifications
    }


def _network_settings(parser, defaults, warnings):
    values = _read_section_values(
        parser,
        "network",
        defaults,
        (
            ("ping_count", "ping_count", int, 1, 20),
            ("ping_timeout_ms", "ping_timeout_ms", int, 100, 10000),
            ("traceroute_max_hops", "traceroute_max_hops", int, 1, 64),
            ("traceroute_timeout_ms", "traceroute_timeout_ms", int, 100, 10000),
            ("command_timeout_seconds", "command_timeout_seconds", float, 1.0, 300.0),
        ),
        warnings,
    )
    values["default_target"] = _read_target(parser, defaults.default_target, warnings)
    return values


def _event_settings(parser, defaults, warnings):
    choices = _read_choices(parser, defaults.event_window_choices, warnings)
    window = _read_value(
        parser,
        "events",
        "default_window_minutes",
        defaults.event_window_minutes,
        int,
        1,
        1440,
        warnings,
    )
    if window not in choices:
        warnings.append(
            "[events] default_window_minutes is not in window_choices; "
            f"using {choices[0]}."
        )
        window = choices[0]
    values = _read_section_values(
        parser,
        "events",
        defaults,
        (
            ("max_events", "max_events", int, 1, 1000),
            ("event_query_timeout_seconds", "query_timeout_seconds", float, 1.0, 300.0),
        ),
        warnings,
    )
    values.update(event_window_minutes=window, event_window_choices=choices)
    return values


def _monitor_settings(parser, defaults, warnings):
    return _read_section_values(
        parser,
        "monitor",
        defaults,
        (
            ("sample_seconds", "sample_seconds", float, 0.2, 60.0),
            ("acpi_refresh_seconds", "acpi_refresh_seconds", float, 1.0, 300.0),
            ("helper_timeout_seconds", "helper_timeout_seconds", float, 1.0, 30.0),
        ),
        warnings,
    )


def _read_config(config_path, warn):
    parser = ConfigParser(interpolation=None)
    try:
        with config_path.open(encoding="utf-8") as config_file:
            parser.read_file(config_file)
    except (OSError, UnicodeError, Error) as exc:
        warn(f"Warning: could not read configuration {config_path}: {exc}")
        return None
    return parser


def load_settings(path=None, warn=print):
    defaults = Settings()
    explicitly_selected = path is not None or bool(environ.get(CONFIG_ENV_VAR))
    config_path = Path(path) if path is not None else default_config_path()
    if not config_path.is_file():
        if explicitly_selected:
            warn(f"Warning: configuration file not found: {config_path}")
        return defaults

    parser = _read_config(config_path, warn)
    if parser is None:
        return defaults

    warnings = []
    values = _network_settings(parser, defaults, warnings)
    values.update(_event_settings(parser, defaults, warnings))
    values.update(_monitor_settings(parser, defaults, warnings))
    for message in warnings:
        warn(f"Warning: {message}")
    return Settings(**values)
