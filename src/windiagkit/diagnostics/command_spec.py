"""An executable command derived from a diagnostic job."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    title: str
    command: tuple
    timeout_seconds: float
    display: str
