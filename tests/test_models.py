"""Tests for data models."""

from datetime import datetime
from time_surfer.models import Day, Span, TrackerResult


class TestSpan:
    def test_span_creation(self):
        span = Span(
            task="coding",
            start=datetime(2026, 1, 30, 9, 0, 0),
            end=datetime(2026, 1, 30, 10, 0, 0),
        )
        assert span.task == "coding"
        assert span.start == datetime(2026, 1, 30, 9, 0, 0)
        assert span.end == datetime(2026, 1, 30, 10, 0, 0)

    def test_span_without_end(self):
        span = Span(
            task="coding",
            start=datetime(2026, 1, 30, 9, 0, 0),
        )
        assert span.end is None


class TestDay:
    def test_day_creation(self):
        day = Day(date="2026-01-30")
        assert day.date == "2026-01-30"
        assert day.start_time is None
        assert day.end_time is None
        assert day.current_task is None
        assert day.spans == []

    def test_day_is_active_when_started_not_stopped(self):
        day = Day(
            date="2026-01-30",
            start_time=datetime(2026, 1, 30, 9, 0, 0),
        )
        assert day.is_active is True

    def test_day_is_not_active_when_not_started(self):
        day = Day(date="2026-01-30")
        assert day.is_active is False

    def test_day_is_not_active_when_stopped(self):
        day = Day(
            date="2026-01-30",
            start_time=datetime(2026, 1, 30, 9, 0, 0),
            end_time=datetime(2026, 1, 30, 17, 0, 0),
        )
        assert day.is_active is False

    def test_day_with_spans(self):
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
        assert len(day.spans) == 1
        assert day.spans[0].task == "coding"


class TestTrackerResult:
    def test_success_result(self):
        result = TrackerResult(success=True, message="Day started")
        assert result.success is True
        assert result.message == "Day started"
        assert result.day is None

    def test_result_with_day(self):
        day = Day(date="2026-01-30")
        result = TrackerResult(success=True, message="Day started", day=day)
        assert result.day is day

    def test_error_result(self):
        result = TrackerResult(success=False, message="Day already started")
        assert result.success is False
        assert result.message == "Day already started"
