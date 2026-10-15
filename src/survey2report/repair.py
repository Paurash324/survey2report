"""Table-level repairs: headers, padding, sentinels and pruning."""

from __future__ import annotations

import pandas as pd

from survey2report.cleaninglog import CleaningLog
from survey2report.coerce import MISSING_SENTINELS, normalise_header


def normalise_headers(df: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    """Rename columns to unique snake_case names.

    Args:
        df: Table with raw headers.
        log: Log that receives the rename entry.

    Returns:
        The table with normalised, deduplicated column names.
    """
    raw = [str(name) for name in df.columns]
    normalised: list[str] = []
    for name in raw:
        candidate = normalise_header(name)
        suffix = 2
        while candidate in normalised:
            candidate = f"{normalise_header(name)}_{suffix}"
            suffix += 1
        normalised.append(candidate)
    renamed = [(old, new) for old, new in zip(raw, normalised, strict=True) if old != new]
    if renamed:
        examples = ", ".join(f"{old} → {new}" for old, new in renamed[:4])
        log.add("inconsistent header", "renamed to snake_case", len(renamed), detail=examples)
    out = df.copy()
    out.columns = normalised
    return out


def normalise_values(df: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    """Strip padding and convert sentinel strings to real missing values.

    Args:
        df: Table of raw text columns.
        log: Log that receives the padding and sentinel entries.

    Returns:
        The table with trimmed values and ``pd.NA`` for placeholders.
    """
    out: dict[str, pd.Series] = {}
    for name in df.columns:
        text = df[name].astype("string")
        stripped = text.str.strip()
        padded = int((stripped != text).sum())
        if padded:
            log.add("whitespace padding", "stripped surrounding whitespace", padded, column=name)
        sentinels = stripped.str.lower().isin(MISSING_SENTINELS).fillna(False)
        sentinel_count = int(sentinels.sum())
        if sentinel_count:
            log.add("sentinel missing value", "treated as missing", sentinel_count, column=name)
        out[name] = stripped.mask(sentinels, pd.NA)
    return pd.DataFrame(out)


def drop_blank_rows(df: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    """Drop rows where every cell is missing.

    Args:
        df: Table to prune.
        log: Log that receives the entry.

    Returns:
        The table without fully blank rows.
    """
    blank = int(df.isna().all(axis=1).sum())
    if blank:
        log.add("blank row", "dropped row", blank)
    return df.dropna(how="all")


def drop_empty_columns(df: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    """Drop columns that hold no data at all.

    Args:
        df: Table to prune.
        log: Log that receives the entry.

    Returns:
        The table without empty columns.
    """
    empty = [name for name in df.columns if bool(df[name].isna().all())]
    if empty:
        log.add("empty column", "dropped column", len(empty), detail=", ".join(empty))
    return df.drop(columns=empty)


def drop_duplicate_rows(df: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    """Drop exact duplicate rows.

    Args:
        df: Table to prune.
        log: Log that receives the entry and the duplicate count.

    Returns:
        The table without duplicate rows.
    """
    duplicates = int(df.duplicated().sum())
    if duplicates:
        log.add("duplicate row", "removed exact duplicate", duplicates)
    log.duplicates_removed = duplicates
    return df.drop_duplicates()
