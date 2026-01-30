"""Shared test fixtures."""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_data_dir(tmp_path):
    """Provide a temporary directory for data storage."""
    return tmp_path / "time-surfer"


@pytest.fixture
def temp_data_file(temp_data_dir):
    """Provide a temporary data file path."""
    return temp_data_dir / "data.json"
