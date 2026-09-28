"""Shared fixtures for the survey2report test suite."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
SAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.csv"))


@pytest.fixture(scope="session")
def examples_dir() -> Path:
    return EXAMPLES_DIR


@pytest.fixture(scope="session")
def sample_files() -> list[Path]:
    assert len(SAMPLE_FILES) == 5, f"expected 5 sample CSVs, found {len(SAMPLE_FILES)}"
    return SAMPLE_FILES


@pytest.fixture
def messy_frame() -> pd.DataFrame:
    """A compact hand-built table with one instance of each defect."""
    return pd.DataFrame(
        {
            "Respondent ID": ["P1", "P2", "P3", "P3", "P3", "", "P5", "P4"],
            " Segment ": [
                "SMB", " smb ", "Enterprise", "Enterprise", "Enterprise", "", "SMB", "café",
            ],
            "Satisfaction": ["4", "3.0", "N/A", "3.0", "3.0", "", "5", ""],
            "nps": ["9/10", "7 out of 10", "", "7", "7", "", "10", "null"],
            "Responded On": [
                "2024-01-05", "05/03/2024", "Jan 9, 2024", "Jan 9, 2024",
                "Jan 9, 2024", "", "2024-02-11", "?",
            ],
            "Spend": ["$1,299.00", "28,3", "149", "149", "149", "", "USD 1250", "-"],
            "comment": [
                "Fine", "Great team", "", "Great team", "Great team", "", "   ", "Needs work",
            ],
        }
    )
