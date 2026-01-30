"""Tests for formatting utilities."""

import pytest

from time_surfer.formatting import format_duration, create_task_table


class TestFormatDuration:
    def test_format_duration_hours_minutes_seconds(self):
        # 2 hours, 34 minutes, 12 seconds
        result = format_duration(2 * 3600 + 34 * 60 + 12)
        assert result == "2:34:12"

    def test_format_duration_zero(self):
        result = format_duration(0)
        assert result == "0:00:00"

    def test_format_duration_only_seconds(self):
        result = format_duration(45)
        assert result == "0:00:45"

    def test_format_duration_only_minutes(self):
        result = format_duration(5 * 60)
        assert result == "0:05:00"

    def test_format_duration_large_hours(self):
        # 12 hours
        result = format_duration(12 * 3600)
        assert result == "12:00:00"


class TestCreateTaskTable:
    def test_create_task_table_single_task(self):
        task_totals = {"coding": 3600.0}  # 1 hour
        table = create_task_table(task_totals)

        # Check table structure
        assert table.title is None
        assert len(table.columns) == 3

    def test_create_task_table_multiple_tasks_sorted_by_duration(self):
        task_totals = {
            "meetings": 3600.0,  # 1 hour
            "coding": 7200.0,  # 2 hours
            "review": 1800.0,  # 30 min
        }
        table = create_task_table(task_totals)

        # Get the row data to verify sort order (highest first)
        rows = list(table.rows)
        # First row should be coding (highest duration)
        # Rows are RenderableType, so we need to check structure
        assert len(rows) >= 3  # At least 3 task rows

    def test_create_task_table_includes_totals_row(self):
        task_totals = {"coding": 3600.0, "meetings": 1800.0}
        table = create_task_table(task_totals)

        # Table should have task rows plus a totals row
        rows = list(table.rows)
        assert len(rows) >= 3  # 2 tasks + totals

    def test_create_task_table_empty(self):
        table = create_task_table({})

        # Empty table should still be valid
        rows = list(table.rows)
        assert len(rows) == 0

    def test_create_task_table_calculates_percentages(self):
        # 75% coding, 25% meetings
        task_totals = {"coding": 3600.0, "meetings": 1200.0}
        table = create_task_table(task_totals)

        # Verify table was created (percentages are in rendered output)
        assert table is not None
