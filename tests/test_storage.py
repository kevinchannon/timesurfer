"""Tests for storage layer."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from time_surfer.models import Day, Span
from time_surfer.storage import Storage


class TestStorage:
    def test_storage_creates_directory_if_missing(self, temp_data_file):
        storage = Storage(temp_data_file)
        storage.save_day(Day(date="2026-01-30"))
        assert temp_data_file.parent.exists()

    def test_save_and_load_day(self, temp_data_file):
        storage = Storage(temp_data_file)
        day = Day(
            date="2026-01-30",
            start_time=datetime(2026, 1, 30, 9, 0, 0),
        )
        storage.save_day(day)

        loaded = storage.load_day("2026-01-30")
        assert loaded is not None
        assert loaded.date == "2026-01-30"
        assert loaded.start_time == datetime(2026, 1, 30, 9, 0, 0)

    def test_load_nonexistent_day_returns_none(self, temp_data_file):
        storage = Storage(temp_data_file)
        loaded = storage.load_day("2026-01-30")
        assert loaded is None

    def test_save_day_with_spans(self, temp_data_file):
        storage = Storage(temp_data_file)
        spans = [
            Span(
                task="coding",
                start=datetime(2026, 1, 30, 9, 0, 0),
                end=datetime(2026, 1, 30, 10, 0, 0),
            ),
        ]
        day = Day(
            date="2026-01-30",
            start_time=datetime(2026, 1, 30, 9, 0, 0),
            spans=spans,
        )
        storage.save_day(day)

        loaded = storage.load_day("2026-01-30")
        assert len(loaded.spans) == 1
        assert loaded.spans[0].task == "coding"
        assert loaded.spans[0].start == datetime(2026, 1, 30, 9, 0, 0)
        assert loaded.spans[0].end == datetime(2026, 1, 30, 10, 0, 0)

    def test_save_multiple_days(self, temp_data_file):
        storage = Storage(temp_data_file)
        day1 = Day(date="2026-01-30", start_time=datetime(2026, 1, 30, 9, 0, 0))
        day2 = Day(date="2026-01-31", start_time=datetime(2026, 1, 31, 9, 0, 0))

        storage.save_day(day1)
        storage.save_day(day2)

        loaded1 = storage.load_day("2026-01-30")
        loaded2 = storage.load_day("2026-01-31")

        assert loaded1.date == "2026-01-30"
        assert loaded2.date == "2026-01-31"

    def test_update_existing_day(self, temp_data_file):
        storage = Storage(temp_data_file)
        day = Day(date="2026-01-30", start_time=datetime(2026, 1, 30, 9, 0, 0))
        storage.save_day(day)

        day.end_time = datetime(2026, 1, 30, 17, 0, 0)
        storage.save_day(day)

        loaded = storage.load_day("2026-01-30")
        assert loaded.end_time == datetime(2026, 1, 30, 17, 0, 0)

    def test_load_from_empty_file(self, temp_data_file):
        temp_data_file.parent.mkdir(parents=True, exist_ok=True)
        temp_data_file.write_text("")
        storage = Storage(temp_data_file)
        loaded = storage.load_day("2026-01-30")
        assert loaded is None

    def test_default_data_path(self):
        storage = Storage()
        expected = Path.home() / ".local" / "share" / "time-surfer" / "data.json"
        assert storage.data_file == expected
