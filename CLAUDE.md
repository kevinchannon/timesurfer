# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

time-surfer is a command-line time tracking tool for Linux that allows quick recording of task durations throughout the working day. The tool is designed for minimal friction: leave it running, switch between tasks, and generate a report at day's end.

## Technology Stack

- **Language**: Python 3.12+
- **Package manager**: uv (for dependency management)
- **CLI framework**: typer (for command definitions)
- **Terminal output**: rich (for colored table output)
- **Config parsing**: PyYAML or ruamel.yaml
- **Platform**: Linux only

## Development Commands

The project uses `uv` for package management. Key commands:

```bash
# Run the main script
python main.py

# Install dependencies (once configured)
uv sync

# Run tests (once test framework is set up)
# TBD - likely pytest
```

## Core Architecture

The application is organized around these key components (as per product spec):

1. **CLI layer** (`cli.py`): Typer-based command definitions for `start`, `stop`, `switch-to`, `show`, and `report`
2. **Tracker logic** (`tracker.py`): Core business logic for time tracking state management
3. **Storage layer** (`storage.py`): JSON persistence to `~/.local/share/time-surfer/data.json`
4. **Configuration** (`config.py`): YAML config loading from `~/.config/time-surfer/config.yaml`
5. **Data models** (`models.py`): Data classes for Day, Span, and related structures

## Data Model

Each day's record contains:
- `date`: ISO date string
- `start_time`: Timestamp when tracking began
- `end_time`: Timestamp when tracking stopped (null if active)
- `current_task`: Name of active task (null if stopped)
- `spans`: List of task spans with `task`, `start`, and `end` timestamps

## Key Behavioral Rules

1. `switch-to` without prior `start` implicitly starts the day
2. Consecutive `switch-to` commands to the same task are no-ops
3. `start` when already started produces an error
4. `stop` when not started produces an error
5. Day overflow handling: Auto-stop previous day at `auto_stop_after_hours` limit if past `day_boundary`

## Configuration Parameters

- `day_boundary`: Time (HH:MM) before which activity counts as previous day (default: "04:00")
- `auto_stop_after_hours`: Auto-close day if duration exceeds this (default: 12)

## Current State

This project is in initial stages with minimal scaffolding. The `main.py` contains only a hello-world placeholder. Implementation should follow the suggested project structure in `requirements/product-spec.md`.
