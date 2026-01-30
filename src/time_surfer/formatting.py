"""Formatting utilities for time-surfer output."""

from rich import box
from rich.table import Table


def format_duration(seconds: float) -> str:
    """Format seconds as H:MM:SS.

    Args:
        seconds: Total seconds to format

    Returns:
        Formatted string like "2:34:12"
    """
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}:{mins:02d}:{secs:02d}"


def create_task_table(task_totals: dict[str, float]) -> Table:
    """Create a rich Table showing tasks, durations, and percentages.

    Args:
        task_totals: Dict mapping task name to total seconds

    Returns:
        Rich Table ready for printing
    """
    table = Table(box=box.HORIZONTALS, show_edge=False)
    table.add_column("Task", style="cyan")
    table.add_column("Duration", justify="right")
    table.add_column("%", justify="right")

    if not task_totals:
        return table

    total_seconds = sum(task_totals.values())

    # Sort by duration descending
    sorted_tasks = sorted(task_totals.items(), key=lambda x: x[1], reverse=True)

    for task, seconds in sorted_tasks:
        duration_str = format_duration(seconds)
        percentage = (seconds / total_seconds * 100) if total_seconds > 0 else 0
        table.add_row(task, duration_str, f"{percentage:.1f}%")

    # Add separator and totals row
    table.add_section()
    table.add_row("Total", format_duration(total_seconds), "100.0%", style="bold")

    return table
