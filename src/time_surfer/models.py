"""Data models for time-surfer."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Span:
    """A span of time spent on a task."""

    task: str
    start: datetime
    end: datetime | None = None


@dataclass
class Day:
    """A day's time tracking record."""

    date: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    current_task: str | None = None
    spans: list[Span] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        """Return True if the day has been started but not stopped."""
        return self.start_time is not None and self.end_time is None


@dataclass
class TrackerResult:
    """Result of a tracker operation."""

    success: bool
    message: str
    day: Day | None = None
