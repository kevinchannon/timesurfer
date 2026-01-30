"""Tests for CLI commands."""

from datetime import datetime
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from time_surfer.cli import app
from time_surfer.storage import Storage


runner = CliRunner()


class TestStartCommand:
    def test_start_succeeds(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        assert "Started tracking at 09:00" in result.output

    def test_start_fails_when_already_started(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                runner.invoke(app, ["start"])
                result = runner.invoke(app, ["start"])

        assert result.exit_code == 1
        assert "Day already started" in result.output


class TestStopCommand:
    def test_stop_succeeds(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                runner.invoke(app, ["start"])
                mock_dt.now.return_value = datetime(2026, 1, 30, 17, 0, 0)
                result = runner.invoke(app, ["stop"])

        assert result.exit_code == 0
        assert "Stopped tracking at 17:00" in result.output
        assert "Total time tracked: 8:00:00" in result.output

    def test_stop_fails_when_not_started(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            result = runner.invoke(app, ["stop"])

        assert result.exit_code == 1
        assert "Day not started" in result.output

    def test_stop_shows_no_tasks_message_when_empty(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                runner.invoke(app, ["start"])
                mock_dt.now.return_value = datetime(2026, 1, 30, 17, 0, 0)
                result = runner.invoke(app, ["stop"])

        assert "No tasks recorded" in result.output

    def test_stop_shows_rich_table_with_tasks(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                runner.invoke(app, ["switch-to", "coding"])
                mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
                result = runner.invoke(app, ["stop"])

        assert result.exit_code == 0
        assert "Stopped tracking at 10:00" in result.output
        assert "Task" in result.output  # Table header
        assert "Duration" in result.output  # Table header
        assert "coding" in result.output


class TestReportCommand:
    def test_report_shows_table(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                runner.invoke(app, ["switch-to", "coding"])
                mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
                result = runner.invoke(app, ["report"])

        assert result.exit_code == 0
        assert "Task" in result.output
        assert "Duration" in result.output
        assert "coding" in result.output

    def test_report_fails_when_no_day(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            result = runner.invoke(app, ["report"])

        assert result.exit_code == 1
        assert "not started" in result.output.lower()

    def test_report_shows_no_tasks_message_when_empty(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                runner.invoke(app, ["start"])
                result = runner.invoke(app, ["report"])

        assert result.exit_code == 0
        assert "No tasks recorded" in result.output


class TestSwitchToCommand:
    def test_switch_to_succeeds(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                runner.invoke(app, ["start"])
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 30, 0)
                result = runner.invoke(app, ["switch-to", "coding"])

        assert result.exit_code == 0
        assert "Switched to 'coding'" in result.output

    def test_switch_to_implicitly_starts(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                result = runner.invoke(app, ["switch-to", "coding"])

        assert result.exit_code == 0
        assert "Switched to 'coding'" in result.output

    def test_switch_to_same_task_is_noop(self, temp_data_file):
        with patch("time_surfer.cli.Storage") as MockStorage:
            MockStorage.return_value = Storage(temp_data_file)
            with patch("time_surfer.tracker.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 1, 30, 9, 0, 0)
                runner.invoke(app, ["switch-to", "coding"])
                mock_dt.now.return_value = datetime(2026, 1, 30, 10, 0, 0)
                result = runner.invoke(app, ["switch-to", "coding"])

        assert result.exit_code == 0
        assert "Already working on 'coding'" in result.output
