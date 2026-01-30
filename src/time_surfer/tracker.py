"""Business logic for time tracking operations."""

from datetime import datetime

from time_surfer.models import Day, Span, TrackerResult
from time_surfer.storage import Storage


class Tracker:
    """Handles time tracking operations."""

    def __init__(self, storage: Storage | None = None):
        self.storage = storage or Storage()

    def start(self) -> TrackerResult:
        """Start tracking for the current day."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        existing_day = self.storage.load_day(date_str)
        if existing_day and existing_day.is_active:
            return TrackerResult(success=False, message="Day already started")

        day = Day(date=date_str, start_time=now)
        self.storage.save_day(day)

        time_str = now.strftime("%H:%M")
        return TrackerResult(
            success=True,
            message=f"Started tracking at {time_str}",
            day=day,
        )

    def stop(self) -> TrackerResult:
        """Stop tracking for the current day."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        day = self.storage.load_day(date_str)
        if not day or not day.is_active:
            return TrackerResult(success=False, message="Day not started")

        # Close any open span
        for span in day.spans:
            if span.end is None:
                span.end = now

        day.end_time = now
        self.storage.save_day(day)

        time_str = now.strftime("%H:%M")
        task_totals = self._aggregate_task_times(day.spans) if day.spans else {}

        return TrackerResult(
            success=True,
            message=f"Stopped tracking at {time_str}",
            day=day,
            task_totals=task_totals,
        )

    def _aggregate_task_times(self, spans: list) -> dict[str, float]:
        """Aggregate total seconds per task from spans."""
        totals: dict[str, float] = {}
        for span in spans:
            if span.end is None:
                continue
            duration = (span.end - span.start).total_seconds()
            if span.task in totals:
                totals[span.task] += duration
            else:
                totals[span.task] = duration
        return totals

    def get_current_day(self) -> Day | None:
        """Get the current active day, if any."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        day = self.storage.load_day(date_str)
        if day and day.is_active:
            return day
        return None

    def get_report_data(self) -> TrackerResult:
        """Get report data for the current day.

        Returns aggregated task times including any open span up to now.
        Works for both active and stopped days.
        """
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        day = self.storage.load_day(date_str)
        if not day or day.start_time is None:
            return TrackerResult(success=False, message="Day not started")

        # Calculate task totals, including open span if any
        task_totals = self._aggregate_task_times_with_open(day.spans, now)

        return TrackerResult(
            success=True,
            message="Report data retrieved",
            day=day,
            task_totals=task_totals,
        )

    def _aggregate_task_times_with_open(
        self, spans: list, now: datetime
    ) -> dict[str, float]:
        """Aggregate total seconds per task from spans, including open spans."""
        totals: dict[str, float] = {}
        for span in spans:
            end_time = span.end if span.end is not None else now
            duration = (end_time - span.start).total_seconds()
            if span.task in totals:
                totals[span.task] += duration
            else:
                totals[span.task] = duration
        return totals

    def switch_to(self, task: str) -> TrackerResult:
        """Switch to a new task, implicitly starting the day if needed."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        day = self.storage.load_day(date_str)

        # Implicitly start if not active
        if not day or not day.is_active:
            day = Day(date=date_str, start_time=now)

        # No-op if same task
        if day.current_task == task:
            return TrackerResult(
                success=True,
                message=f"Already working on '{task}'",
                day=day,
            )

        # Close current span if exists
        if day.current_task is not None:
            for span in day.spans:
                if span.end is None:
                    span.end = now
                    break

        # Create new span
        new_span = Span(task=task, start=now)
        day.spans.append(new_span)
        day.current_task = task

        self.storage.save_day(day)

        time_str = now.strftime("%H:%M")
        return TrackerResult(
            success=True,
            message=f"Switched to '{task}' at {time_str}",
            day=day,
        )
