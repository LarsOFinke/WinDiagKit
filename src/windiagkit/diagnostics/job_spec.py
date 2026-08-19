"""Metadata for a selectable diagnostic job."""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobSpec:
    key: str
    category: str
    title: str
    description: str
    needs_target: bool = False
    uses_event_window: bool = False
