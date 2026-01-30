"""CLI commands for time-surfer."""

import typer
from rich.console import Console

from time_surfer.formatting import create_task_table, format_duration
from time_surfer.storage import Storage
from time_surfer.tracker import Tracker

app = typer.Typer(help="A command-line time tracking tool.")
console = Console()


def get_tracker() -> Tracker:
    """Create a tracker with default storage."""
    return Tracker(Storage())


@app.command()
def start():
    """Start tracking time for the day."""
    tracker = get_tracker()
    result = tracker.start()

    if result.success:
        console.print(f"[green]{result.message}[/green]")
    else:
        console.print(f"[red]Error: {result.message}[/red]")
        raise typer.Exit(code=1)


@app.command()
def stop():
    """Stop tracking time and show daily summary."""
    tracker = get_tracker()
    result = tracker.stop()

    if not result.success:
        console.print(f"[red]Error: {result.message}[/red]")
        raise typer.Exit(code=1)

    console.print(f"[green]{result.message}[/green]")

    # Calculate total time tracked
    if result.day and result.day.start_time and result.day.end_time:
        total_seconds = (result.day.end_time - result.day.start_time).total_seconds()
        console.print(f"Total time tracked: {format_duration(total_seconds)}")

    if not result.task_totals:
        console.print("No tasks recorded. Use 'switch-to' to track tasks.")
        return

    table = create_task_table(result.task_totals)
    console.print(table)


@app.command("switch-to")
def switch_to(task: str = typer.Argument(..., help="Name of the task to switch to")):
    """Switch to a new task (starts day if needed)."""
    tracker = get_tracker()
    result = tracker.switch_to(task)

    if result.success:
        console.print(f"[green]{result.message}[/green]")
    else:
        console.print(f"[red]Error: {result.message}[/red]")
        raise typer.Exit(code=1)


@app.command()
def report():
    """Show time report for the current day."""
    tracker = get_tracker()
    result = tracker.get_report_data()

    if not result.success:
        console.print(f"[red]Error: {result.message}[/red]")
        raise typer.Exit(code=1)

    if not result.task_totals:
        console.print("No tasks recorded. Use 'switch-to' to track tasks.")
        return

    table = create_task_table(result.task_totals)
    console.print(table)


if __name__ == "__main__":
    app()
