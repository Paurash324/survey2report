"""Tests for coercion, column type detection and the cleaning log."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from survey2report.cleaner import (
    clean_csv,
    clean_dataframe,
    detect_column_type,
    load_csv,
    save_cleaned,
)
from survey2report.coerce import canonical_labels, normalise_header, parse_number
from survey2report.dates import parse_date

EXPECTED_TYPES: dict[str, dict[str, str]] = {
    "employee_engagement_2024.csv": {
        "employee_id": "text",
        "department": "categorical",
        "tenure_yrs": "numeric",
        "role": "categorical",
        "engagement_score": "numeric",
        "manager_support": "numeric",
        "would_recommend": "categorical",
        "survey_date": "date",
        "comments": "text",
    },
    "customer_satisfaction_q1.csv": {
        "response_id": "text",
        "customer_name": "text",
        "plan": "categorical",
        "nps_score": "numeric",
        "satisfaction_1_5": "numeric",
        "support_tickets": "numeric",
        "annual_spend": "numeric",
        "churn_risk": "categorical",
        "response_date": "date",
        "feedback": "text",
    },
    "event_feedback.csv": {
        "reg_id": "text",
        "attendee_name": "text",
        "session_rating": "numeric",
        "speaker_rating": "numeric",
        "would_attend_again": "categorical",
        "session_length_mins": "numeric",
        "feedback_date": "date",
        "city": "categorical",
        "notes": "text",
    },
    "product_pricing_survey.csv": {
        "respondent_id": "text",
        "segment": "categorical",
        "willingness_to_pay": "numeric",
        "purchase_intent": "categorical",
        "price_shown": "numeric",
        "discount_pct": "numeric",
        "interview_date": "date",
        "decision_maker": "categorical",
        "verbatim": "text",
    },
    "public_health_checkup.csv": {
        "patient_id": "text",
        "visit_date": "date",
        "age": "numeric",
        "sex": "categorical",
        "bmi": "numeric",
        "systolic_bp": "numeric",
        "smoker": "categorical",
        "exercise_days_per_week": "numeric",
        "notes": "text",
    },
}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("$1,299.00", 1299.0),
        ("1,250", 1250.0),
        ("28,3", 28.3),
        ("45 min", 45.0),
        ("20 %", 20.0),
        ("USD 1250", 1250.0),
        ("-3.5", -3.5),
        ("3 - Neutral", 3.0),
        ("9/10", 9.0),
        ("N/A", None),
        ("REG-2000", 2000.0),
        ("", None),
        ("   ", None),
        ("none", None),
    ],
)
def test_parse_number(raw: str, expected: float | None) -> None:
    assert parse_number(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2024-04-01", datetime(2024, 4, 1)),
        ("01-Sep-2024", datetime(2024, 9, 1)),
        ("Jun 12, 2024", datetime(2024, 6, 12)),
        ("06/23/2024", datetime(2024, 6, 23)),
        ("05/03/2024", datetime(2024, 3, 5)),
        ("2024-01-05 08:30:00", datetime(2024, 1, 5, 8, 30)),
        ("?", None),
        ("N/A", None),
        ("", None),
    ],
)
def test_parse_date(raw: str, expected: datetime | None) -> None:
    assert parse_date(raw) == expected


def test_normalise_header() -> None:
    assert normalise_header("Department ") == "department"
    assert normalise_header("satisfaction_(1-5)") == "satisfaction_1_5"
    assert normalise_header("Would attend again?") == "would_attend_again"
    assert normalise_header("  ") == "column"


def test_canonical_labels_uses_most_common_spelling() -> None:
    # "smb" is the most frequent spelling, so it wins over "SMB".
    labels = canonical_labels(pd.Series(["SMB", " smb ", "smb", "Enterprise"], dtype="string"))
    assert list(labels) == ["smb", "smb", "smb", "Enterprise"]
    casing = canonical_labels(pd.Series(["Yes", " yes ", "YES", pd.NA], dtype="string"))
    assert list(casing)[:3] == ["Yes", "Yes", "Yes"]
    # Y/N and 1/0 answers collapse onto the same boolean labels.
    binary = canonical_labels(pd.Series(["Y", "yes", "1", "N", "0", "no"], dtype="string"))
    assert list(binary) == ["Yes", "Yes", "Yes", "No", "No", "No"]


def test_detect_column_type_on_single_columns() -> None:
    assert detect_column_type(pd.Series(["1", "2", "3"]), "score") == "numeric"
    assert detect_column_type(pd.Series(["2024-01-01", "2024-02-01"]), "seen") == "date"
    assert detect_column_type(pd.Series(["A", "B", "A", "B"]), "bucket") == "categorical"
    assert detect_column_type(pd.Series([f"free text {i}" for i in range(50)]), "why") == "text"
    assert detect_column_type(pd.Series([pd.NA, pd.NA]), "empty") == "text"


def test_detect_column_type_keeps_identifiers_and_prose_as_text() -> None:
    assert detect_column_type(pd.Series(["REG-2000", "REG-2001"]), "reg_id") == "text"
    assert detect_column_type(pd.Series(["Ada", "Grace"]), "customer_name") == "text"
    assert detect_column_type(pd.Series(["nice", "slow"]), "feedback_date") == "text"
    assert detect_column_type(pd.Series(["2024-01-01", "2024-02-01"]), "feedback_date") == "date"


def test_clean_dataframe_repairs_every_defect(messy_frame: pd.DataFrame) -> None:
    clean, log = clean_dataframe(messy_frame, filename="messy.csv")

    assert list(clean.columns) == [
        "respondent_id",
        "segment",
        "satisfaction",
        "nps",
        "responded_on",
        "spend",
        "comment",
    ]
    assert log.rows_in == 8
    assert log.rows_out == 6
    assert log.duplicates_removed == 1
    assert list(clean["segment"]) == ["SMB", "SMB", "Enterprise", "Enterprise", "SMB", "café"]
    assert clean["satisfaction"].tolist()[:2] == [4.0, 3.0]
    assert clean["nps"].iloc[0] == 9.0
    assert clean["spend"].iloc[1] == 28.3
    assert clean["spend"].iloc[0] == 1299.0
    assert clean["responded_on"].iloc[1] == pd.Timestamp("2024-03-05")
    assert pd.isna(clean["comment"].iloc[2])
    assert log.missing_before > log.missing_after > 0
    assert log.types["respondent_id"] == "text"
    assert log.type_counts["numeric"] == 3
    issues = log.issues()
    assert issues[0] == "inconsistent header"
    assert {
        "whitespace padding",
        "sentinel missing value",
        "duplicate row",
        "mixed date formats",
    } <= set(issues)


def test_cleaning_log_markdown_and_summary(messy_frame: pd.DataFrame) -> None:
    _, log = clean_dataframe(messy_frame, filename="messy.csv")
    markdown = log.to_markdown()

    assert markdown.startswith("# Cleaning log — messy.csv")
    assert "## Detected column types" in markdown
    assert "## Actions taken" in markdown
    assert "| `segment` | categorical |" in markdown
    assert len(log.quality_summary()) >= 3


def test_cleaning_log_can_be_written_to_disk(messy_frame: pd.DataFrame, tmp_path: Path) -> None:
    _, log = clean_dataframe(messy_frame, filename="messy.csv")
    written = log.write(tmp_path / "nested" / "cleaning_log.md")
    assert written.read_text(encoding="utf-8") == log.to_markdown()


def test_save_cleaned_writes_iso_dates(messy_frame: pd.DataFrame, tmp_path: Path) -> None:
    clean, _ = clean_dataframe(messy_frame, filename="messy.csv")
    path = save_cleaned(clean, tmp_path / "clean.csv")
    text = path.read_text(encoding="utf-8")
    assert "2024-03-05" in text
    assert "Jan 9, 2024" not in text


@pytest.mark.parametrize("filename", sorted(EXPECTED_TYPES))
def test_samples_clean_with_expected_types(
    filename: str, examples_dir: Path, sample_files: list[Path]
) -> None:
    assert any(path.name == filename for path in sample_files)
    clean, log = clean_csv(examples_dir / filename)

    assert log.rows_out <= log.rows_in
    assert list(log.types) == list(clean.columns)
    assert log.types == EXPECTED_TYPES[filename]
    assert log.rows_out > 100
    assert clean.notna().to_numpy().mean() > 0.5


def test_load_csv_strips_byte_order_mark(examples_dir: Path) -> None:
    frame = load_csv(examples_dir / "event_feedback.csv")
    assert list(frame.columns)[0] == "Reg ID"
    assert not any(name.startswith("\ufeff") for name in frame.columns)
