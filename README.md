# time-surfer

A command-line time tracking tool for Linux. Designed for minimal friction: leave it running, switch between tasks, generate a report at day's end.

## Installation

Requires Python 3.12+.

```bash
uv sync
```

## Usage

```bash
# Start tracking for the day
time-surfer start

# Switch to a task (starts the day if not already running)
time-surfer switch-to "code review"

# Switch to another task
time-surfer switch-to "feature work"

# Show current status
time-surfer show

# Generate a summary report
time-surfer report

# Stop tracking
time-surfer stop
```

## Report Output

```
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ Task               ┃ Duration ┃      % ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ Feature X          │  2:34:12 │  38.2% │
│ Code review        │  1:45:00 │  26.1% │
│ Meetings           │  1:12:33 │  18.0% │
├────────────────────┼──────────┼────────┤
│ Total              │  5:31:45 │ 100.0% │
└────────────────────┴──────────┴────────┘
```

## Configuration

Config file: `~/.config/time-surfer/config.yaml`

```yaml
day_boundary: "04:00"      # Time before which activity counts as previous day
auto_stop_after_hours: 12  # Auto-close day if it exceeds this duration
```

## Data Storage

Data is stored in `~/.local/share/time-surfer/data.json`.

## Development

```bash
# Run tests
uv run pytest

# Run the CLI directly
uv run time-surfer --help
```
