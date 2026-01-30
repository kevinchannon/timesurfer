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


def create_task_table(
    task_totals: dict[str, float],
    total_duration: float | None = None,
) -> Table:
    """Create a rich Table showing tasks, durations, and percentages.

    Args:
        task_totals: Dict mapping task name to total seconds
        total_duration: Total duration in seconds (if provided, used to calculate
            untracked time and percentages)

    Returns:
        Rich Table ready for printing
    """
    table = Table(box=box.HORIZONTALS, show_edge=False)
    table.add_column("Task", style="cyan")
    table.add_column("Duration", justify="right")
    table.add_column("%", justify="right")

    if not task_totals and total_duration is None:
        return table

    task_sum = sum(task_totals.values())

    # Use total_duration if provided, otherwise use sum of tasks
    base_duration = total_duration if total_duration is not None else task_sum

    # Sort by duration descending
    sorted_tasks = sorted(task_totals.items(), key=lambda x: x[1], reverse=True)

    for task, seconds in sorted_tasks:
        duration_str = format_duration(seconds)
        percentage = (seconds / base_duration * 100) if base_duration > 0 else 0
        table.add_row(task, duration_str, f"{percentage:.1f}%")

    # Calculate and show untracked time if total_duration provided
    if total_duration is not None:
        untracked = total_duration - task_sum
        # Only show if >= 0.5 seconds (handles floating point errors)
        if untracked >= 0.5:
            percentage = (untracked / base_duration * 100) if base_duration > 0 else 0
            table.add_row("untracked", format_duration(untracked), f"{percentage:.1f}%")

    # Add separator and totals row
    table.add_section()
    table.add_row("Total", format_duration(base_duration), "100.0%", style="bold")

    return table
