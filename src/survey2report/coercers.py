"""Per-column coercers that turn a typed column into clean values.

Each coercer receives the :class:`~survey2report.cleaninglog.CleaningLog` and
records what it repaired, so the cleaner itself stays a short pipeline.
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from survey2report.cleaninglog import CleaningLog, ColumnType
from survey2report.coerce import (
    canonical_labels,
    count_variant_groups,
    is_plain_number,
    parse_number,
)
from survey2report.dates import count_slash_dates, is_iso_date, parse_date

ColumnCleaner = Callable[[pd.Series, str, CleaningLog], pd.Series]


def clean_numeric(series: pd.Series, name: str, log: CleaningLog) -> pd.Series:
    """Extract numbers from a column of messy numeric text.

    Args:
        series: Raw column.
        name: Column name, used in log entries.
        log: Log that receives the entries.

    Returns:
        Float column, with unparseable cells left missing.
    """
    text = series.astype("string")
    parsed = pd.to_numeric(text.map(parse_number), errors="coerce")
    present = text.notna()
    repaired = int((present & ~text.map(is_plain_number).fillna(False) & parsed.notna()).sum())
    if repaired:
        log.add(
            "messy numeric text",
            "extracted value from units, currency or separators",
            repaired,
            column=name,
        )
    failed = int((present & parsed.isna()).sum())
    if failed:
        log.add("unparseable number", "left value blank", failed, column=name)
    return parsed


def clean_dates(series: pd.Series, name: str, log: CleaningLog) -> pd.Series:
    """Parse a column of dates written in several formats into ISO dates.

    Args:
        series: Raw column.
        name: Column name, used in log entries.
        log: Log that receives the entries.

    Returns:
        Datetime column, with unparseable cells left missing.
    """
    text = series.astype("string")
    parsed = pd.to_datetime(list(text.map(parse_date)), errors="coerce")
    dates = pd.Series(parsed, index=series.index)
    slash = count_slash_dates(text)
    if slash:
        log.add(
            "ambiguous DD/MM vs MM/DD",
            "read day-first unless month-first is forced",
            slash,
            column=name,
        )
    normalised = int((dates.notna() & ~text.map(is_iso_date).fillna(False)).sum())
    if normalised:
        log.add("mixed date formats", "parsed to ISO date (YYYY-MM-DD)", normalised, column=name)
    failed = int((dates.isna() & text.notna()).sum())
    if failed:
        log.add("unparseable date", "left date blank", failed, column=name)
    return dates


def clean_categorical(series: pd.Series, name: str, log: CleaningLog) -> pd.Series:
    """Collapse casing and spelling variants of a categorical column.

    Args:
        series: Raw column.
        name: Column name, used in log entries.
        log: Log that receives the entries.

    Returns:
        Column where every variant maps to its most common spelling.
    """
    variants = count_variant_groups(series)
    if variants:
        log.add(
            "inconsistent category spelling",
            "standardised to most common spelling",
            variants,
            column=name,
        )
    return canonical_labels(series)


def clean_text(series: pd.Series, name: str, log: CleaningLog) -> pd.Series:
    """Keep free text as trimmed strings.

    Args:
        series: Raw column.
        name: Column name, unused but kept for a uniform signature.
        log: Log, unused but kept for a uniform signature.

    Returns:
        The column as trimmed strings.
    """
    return series.astype("string")


COERCERS: dict[ColumnType, ColumnCleaner] = {
    "numeric": clean_numeric,
    "date": clean_dates,
    "categorical": clean_categorical,
    "text": clean_text,
}
