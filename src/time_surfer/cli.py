"""CLI commands for time-surfer."""

import typer
from rich.console import Console

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

    if result.success:
        console.print(f"[green]{result.message}[/green]")
    else:
        console.print(f"[red]Error: {result.message}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
