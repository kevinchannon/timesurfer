"""Business logic for time tracking operations."""

from datetime import datetime

from time_surfer.models import Day, TrackerResult
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

        day.end_time = now
        self.storage.save_day(day)

        time_str = now.strftime("%H:%M")
        total_time = day.end_time - day.start_time
        total_hours = int(total_time.total_seconds() // 3600)
        total_minutes = int((total_time.total_seconds() % 3600) // 60)
        total_seconds = int(total_time.total_seconds() % 60)
        total_str = f"{total_hours}:{total_minutes:02d}:{total_seconds:02d}"

        message = f"Stopped tracking at {time_str}\n\n"
        message += "Daily Summary\n"
        message += f"Total time tracked: {total_str}\n"

        if not day.spans:
            message += "No tasks recorded. Use 'switch-to' to track tasks."

        return TrackerResult(
            success=True,
            message=message,
            day=day,
        )

    def get_current_day(self) -> Day | None:
        """Get the current active day, if any."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        day = self.storage.load_day(date_str)
        if day and day.is_active:
            return day
        return None
