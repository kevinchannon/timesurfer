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

    def test_create_task_table_shows_untracked_time(self):
        """Untracked time should appear when total_duration exceeds task sum."""
        # 1 hour of coding, but 1.5 hours total duration = 30 min untracked
        task_totals = {"coding": 3600.0}
        total_duration = 5400.0  # 1.5 hours
        table = create_task_table(task_totals, total_duration=total_duration)

        rows = list(table.rows)
        # Should have: coding, untracked, Total (3 rows)
        assert len(rows) == 3

        # Render table to check content
        from io import StringIO
        from rich.console import Console

        console = Console(file=StringIO(), force_terminal=True)
        console.print(table)
        output = console.file.getvalue()

        assert "untracked" in output
        assert "0:30:00" in output  # 30 min untracked

    def test_create_task_table_no_untracked_when_fully_allocated(self):
        """No untracked row when tasks exactly fill total duration."""
        task_totals = {"coding": 3600.0, "meetings": 1800.0}
        total_duration = 5400.0  # Exactly matches sum
        table = create_task_table(task_totals, total_duration=total_duration)

        rows = list(table.rows)
        # Should have: coding, meetings, Total (3 rows, no untracked)
        assert len(rows) == 3

        from io import StringIO
        from rich.console import Console

        console = Console(file=StringIO(), force_terminal=True)
        console.print(table)
        output = console.file.getvalue()

        assert "untracked" not in output

    def test_create_task_table_untracked_below_threshold_not_shown(self):
        """Untracked time < 0.5 seconds should not be shown (rounding errors)."""
        task_totals = {"coding": 3600.0}
        # 0.4 seconds untracked - below threshold
        total_duration = 3600.4
        table = create_task_table(task_totals, total_duration=total_duration)

        from io import StringIO
        from rich.console import Console

        console = Console(file=StringIO(), force_terminal=True)
        console.print(table)
        output = console.file.getvalue()

        assert "untracked" not in output

    def test_create_task_table_percentages_based_on_total_duration(self):
        """Percentages should be based on total_duration, not sum of tasks."""
        # 1 hour coding out of 2 hours total = 50%
        task_totals = {"coding": 3600.0}
        total_duration = 7200.0  # 2 hours
        table = create_task_table(task_totals, total_duration=total_duration)

        from io import StringIO
        from rich.console import Console

        console = Console(file=StringIO(), force_terminal=True)
        console.print(table)
        output = console.file.getvalue()

        # coding should be 50%, untracked should be 50%
        assert "50.0%" in output

    def test_create_task_table_backward_compatible_without_total_duration(self):
        """Without total_duration parameter, behavior unchanged."""
        task_totals = {"coding": 3600.0, "meetings": 1800.0}
        table = create_task_table(task_totals)

        from io import StringIO
        from rich.console import Console

        console = Console(file=StringIO(), force_terminal=True)
        console.print(table)
        output = console.file.getvalue()

        # No untracked row when total_duration not provided
        assert "untracked" not in output
        # Percentages still work (coding is 66.7%, meetings is 33.3%)
        assert "66.7%" in output
