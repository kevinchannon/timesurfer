"""JSON persistence for time-surfer data."""

import json
from datetime import datetime
from pathlib import Path

from time_surfer.models import Day, Span


class Storage:
    """Handles persistence of time tracking data to JSON."""

    DEFAULT_DATA_PATH = Path.home() / ".local" / "share" / "time-surfer" / "data.json"

    def __init__(self, data_file: Path | None = None):
        self.data_file = data_file or self.DEFAULT_DATA_PATH

    def save_day(self, day: Day) -> None:
        """Save a day's data to storage."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        data = self._load_all_data()
        data[day.date] = self._day_to_dict(day)

        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def load_day(self, date: str) -> Day | None:
        """Load a day's data from storage. Returns None if not found."""
        data = self._load_all_data()
        if date not in data:
            return None
        return self._dict_to_day(data[date])

    def _load_all_data(self) -> dict:
        """Load all data from the JSON file."""
        if not self.data_file.exists():
            return {}
        try:
            with open(self.data_file) as f:
                content = f.read()
                if not content.strip():
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            return {}

    def _day_to_dict(self, day: Day) -> dict:
        """Convert a Day object to a dictionary."""
        return {
            "date": day.date,
            "start_time": day.start_time.isoformat() if day.start_time else None,
            "end_time": day.end_time.isoformat() if day.end_time else None,
            "current_task": day.current_task,
            "spans": [self._span_to_dict(span) for span in day.spans],
        }

    def _dict_to_day(self, data: dict) -> Day:
        """Convert a dictionary to a Day object."""
        return Day(
            date=data["date"],
            start_time=datetime.fromisoformat(data["start_time"]) if data["start_time"] else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            current_task=data.get("current_task"),
            spans=[self._dict_to_span(s) for s in data.get("spans", [])],
        )

    def _span_to_dict(self, span: Span) -> dict:
        """Convert a Span object to a dictionary."""
        return {
            "task": span.task,
            "start": span.start.isoformat(),
            "end": span.end.isoformat() if span.end else None,
        }

    def _dict_to_span(self, data: dict) -> Span:
        """Convert a dictionary to a Span object."""
        return Span(
            task=data["task"],
            start=datetime.fromisoformat(data["start"]),
            end=datetime.fromisoformat(data["end"]) if data["end"] else None,
        )
