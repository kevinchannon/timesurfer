# time-surfer: Minimal Product Specification

## Overview

A command-line time tracking tool for Linux that allows quick recording of task durations throughout the working day. Designed for minimal friction - leave it running, switch between tasks, generate a report at day's end.

## Core Commands

| Command | Description |
|---------|-------------|
| `time-surfer start` | Begin tracking for the day |
| `time-surfer switch-to "task name"` | Switch to a named task (starts timer if not already running) |
| `time-surfer show` | Display current status: active task, elapsed time on current task, total time today |
| `time-surfer stop` | End tracking for the day |
| `time-surfer report` | Output a table summarising time spent per task (aggregated), with terminal colours |

## Data Model

Each day's record contains:

- `date`: ISO date string
- `start_time`: Timestamp when tracking began
- `end_time`: Timestamp when tracking stopped (null if active)
- `current_task`: Name of active task (null if stopped)
- `spans`: List of task spans, each with:
  - `task`: Task name
  - `start`: Timestamp
  - `end`: Timestamp (null if current span)

## Storage

- **Format**: JSON
- **Location**: `~/.local/share/time-surfer/data.json`
- Store multiple days in a single file (or one file per day - implementer's choice)

## Configuration

- **Format**: YAML
- **Location**: `~/.config/time-surfer/config.yaml`
- **Parameters**:
  - `day_boundary`: Time (HH:MM) before which activity counts as previous day. Default: `"04:00"`
  - `auto_stop_after_hours`: Automatically close a day if it exceeds this duration. Default: `12`

## Behavioural Rules

1. **`switch-to` without `start`**: Implicitly start the day, then switch to the task
2. **Consecutive `switch-to` to same task**: No-op (continue current span)
3. **`start` when already started**: Error message, no state change
4. **`stop` when not started**: Error message, no state change
5. **Day overflow handling**: If current time is past `day_boundary` and a previous day is still open, auto-stop it at the configured `auto_stop_after_hours` limit

## Report Output

The `report` command outputs a table to the terminal:

- Columns: Task name, Total time (HH:MM:SS or similar), Percentage of day
- Sorted by total time descending
- Use terminal colours for visual clarity (e.g., via `rich`)
- Include a totals row

Example:

```
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ Task               ┃ Duration ┃      % ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ Feature X          │  2:34:12 │  38.2% │
│ Code review        │  1:45:00 │  26.1% │
│ Meetings           │  1:12:33 │  18.0% │
│ Email              │  0:45:15 │  11.2% │
│ Admin              │  0:26:00 │   6.5% │
├────────────────────┼──────────┼────────┤
│ Total              │  6:43:00 │ 100.0% │
└────────────────────┴──────────┴────────┘
```

## Technology Stack

- **Language**: Python 3.11+
- **Package manager**: uv
- **CLI framework**: typer
- **Terminal output**: rich
- **Config parsing**: PyYAML (or ruamel.yaml)

## Project Structure (Suggested)

```
time-surfer/
├── pyproject.toml
├── src/
│   └── time_surfer/
│       ├── __init__.py
│       ├── cli.py          # Typer app, command definitions
│       ├── tracker.py      # Core logic: start, stop, switch, report
│       ├── storage.py      # JSON persistence
│       ├── config.py       # YAML config loading
│       └── models.py       # Data classes for Day, Span, etc.
└── tests/
    └── ...
```

## Out of Scope (Future)

- Activity/idle detection daemon
- GUI or TUI interactive mode
- Cloud sync
- Multiple concurrent timers
- Historical reporting across multiple days
