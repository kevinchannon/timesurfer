"""Tests for tracker logic."""

from datetime import datetime
from unittest.mock import patch

import pytest

from time_surfer.models import Day, Span
from time_surfer.storage import Storage
from time_surfer.tracker import Tracker


class TestTrackerStart:
    def test_start_creates_day_with_timestamp(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            mock_dt.fromisoformat = datetime.fromisoformat
            result = tracker.start()

        assert result.success is True
        assert result.message == "Started tracking at 09:00"
        assert result.day is not None
        assert result.day.start_time == datetime(2026, 1, 30, 9, 0, 0)
        assert result.day.date == "2026-01-30"

    def test_start_persists_day(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()

        loaded = storage.load_day("2026-01-30")
        assert loaded is not None
        assert loaded.start_time == datetime(2026, 1, 30, 9, 0, 0)

    def test_start_fails_when_already_started(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            result = tracker.start()

        assert result.success is False
        assert result.message == "Day already started"

    def test_start_succeeds_after_previous_day_stopped(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        # Start and stop on day 1
        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            mock_dt.now.return_value = datetime(2026, 1, 30, 17, 0, 0)
            tracker.stop()

        # Start on day 2
        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 31, 9, 0, 0)
            result = tracker.start()

        assert result.success is True


class TestTrackerStop:
    def test_stop_sets_end_time(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            mock_dt.now.return_value = datetime(2026, 1, 30, 17, 0, 0)
            result = tracker.stop()

        assert result.success is True
        assert "Stopped tracking at 17:00" in result.message
        assert result.day.end_time == datetime(2026, 1, 30, 17, 0, 0)

    def test_stop_fails_when_not_started(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        result = tracker.stop()

        assert result.success is False
        assert result.message == "Day not started"

    def test_stop_persists_end_time(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            mock_dt.now.return_value = datetime(2026, 1, 30, 17, 0, 0)
            tracker.stop()

        loaded = storage.load_day("2026-01-30")
        assert loaded.end_time == datetime(2026, 1, 30, 17, 0, 0)

    def test_stop_returns_task_totals(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.switch_to("coding")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
            result = tracker.stop()

        assert result.task_totals is not None
        assert "coding" in result.task_totals
        assert result.task_totals["coding"] == 3600.0  # 1 hour

    def test_stop_with_no_spans_returns_empty_task_totals(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            mock_dt.now.return_value = datetime(2026, 1, 30, 17, 0, 0)
            result = tracker.stop()

        assert result.task_totals == {}

    def test_stop_returns_multiple_task_totals(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 30, 0)
            tracker.switch_to("coding")
            mock_dt.now.return_value = datetime(2026, 1, 30, 11, 30, 0)
            tracker.switch_to("meetings")
            mock_dt.now.return_value = datetime(2026, 1, 30, 12, 0, 0)
            result = tracker.stop()

        assert result.task_totals["coding"] == 7200.0  # 2 hours
        assert result.task_totals["meetings"] == 1800.0  # 30 min

    def test_stop_aggregates_multiple_spans_same_task(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.switch_to("coding")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
            tracker.switch_to("meetings")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 30, 0)
            tracker.switch_to("coding")  # back to coding
            mock_dt.now.return_value = datetime(2026, 1, 30, 11, 30, 0)
            result = tracker.stop()

        # coding: 1hr + 1hr = 2hrs, meetings: 30min
        assert result.task_totals["coding"] == 7200.0
        assert result.task_totals["meetings"] == 1800.0

    def test_stop_closes_open_span(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.switch_to("coding")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
            result = tracker.stop()

        # The open span should be closed at stop time
        assert result.day.spans[0].end == datetime(2026, 1, 30, 10, 0, 0)


class TestTrackerGetCurrentDay:
    def test_get_current_day_returns_active_day(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            day = tracker.get_current_day()

        assert day is not None
        assert day.is_active is True

    def test_get_current_day_returns_none_when_not_started(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        day = tracker.get_current_day()
        assert day is None

    def test_get_current_day_returns_none_when_stopped(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            mock_dt.now.return_value = datetime(2026, 1, 30, 17, 0, 0)
            tracker.stop()
            day = tracker.get_current_day()

        assert day is None


class TestTrackerGetReportData:
    def test_get_report_data_returns_aggregated_times(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.switch_to("coding")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
            tracker.switch_to("meetings")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 30, 0)
            result = tracker.get_report_data()

        assert result.success is True
        assert result.task_totals is not None
        assert "coding" in result.task_totals
        assert result.task_totals["coding"] == 3600.0  # 1 hour

    def test_get_report_data_includes_open_span(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.switch_to("coding")
            # Don't switch away - span is still open
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
            result = tracker.get_report_data()

        assert result.success is True
        assert result.task_totals["coding"] == 3600.0  # 1 hour up to "now"

    def test_get_report_data_fails_when_no_day(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        result = tracker.get_report_data()

        assert result.success is False
        assert "not started" in result.message.lower()

    def test_get_report_data_with_stopped_day(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.switch_to("coding")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
            tracker.stop()
            result = tracker.get_report_data()

        assert result.success is True
        assert result.task_totals["coding"] == 3600.0


class TestTrackerSwitchTo:
    def test_switch_to_creates_span_when_day_active(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 30, 0)
            result = tracker.switch_to("coding")

        assert result.success is True
        assert "Switched to 'coding'" in result.message
        assert result.day is not None
        assert len(result.day.spans) == 1
        assert result.day.spans[0].task == "coding"
        assert result.day.spans[0].start == datetime(2026, 1, 30, 9, 30, 0)
        assert result.day.current_task == "coding"

    def test_switch_to_implicitly_starts_day(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            result = tracker.switch_to("coding")

        assert result.success is True
        assert result.day is not None
        assert result.day.is_active is True
        assert result.day.start_time == datetime(2026, 1, 30, 9, 0, 0)
        assert len(result.day.spans) == 1
        assert result.day.spans[0].task == "coding"

    def test_switch_to_same_task_is_noop(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 30, 0)
            tracker.switch_to("coding")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
            result = tracker.switch_to("coding")

        assert result.success is True
        assert "Already working on 'coding'" in result.message
        assert len(result.day.spans) == 1

    def test_switch_to_closes_previous_span(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.start()
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 30, 0)
            tracker.switch_to("coding")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
            result = tracker.switch_to("meetings")

        assert result.day.spans[0].end == datetime(2026, 1, 30, 10, 0, 0)
        assert result.day.spans[1].task == "meetings"
        assert result.day.spans[1].end is None

    def test_switch_to_persists_changes(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.switch_to("coding")

        loaded = storage.load_day("2026-01-30")
        assert loaded is not None
        assert len(loaded.spans) == 1
        assert loaded.spans[0].task == "coding"
        assert loaded.current_task == "coding"

    def test_multiple_switches_create_multiple_spans(self, temp_data_file):
        storage = Storage(temp_data_file)
        tracker = Tracker(storage)

        with patch("time_surfer.tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
            tracker.switch_to("coding")
            mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
            tracker.switch_to("meetings")
            mock_dt.now.return_value = datetime(2026, 1, 30, 11, 0, 0)
            result = tracker.switch_to("review")

        assert len(result.day.spans) == 3
        assert result.day.spans[0].task == "coding"
        assert result.day.spans[1].task == "meetings"
        assert result.day.spans[2].task == "review"
        assert result.day.current_task == "review"
