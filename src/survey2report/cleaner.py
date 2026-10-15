"""Load messy survey CSVs, detect column types and clean them.

The cleaner is deliberately conservative: it repairs what it can prove is
repairable, records every change in a :class:`~survey2report.cleaninglog.CleaningLog`,
and only drops data that carries no information (blank rows, empty columns,
exact duplicate rows).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from survey2report.cleaninglog import CleaningLog, ColumnType
from survey2report.coerce import is_missing, is_number_like, parse_number
from survey2report.coercers import COERCERS
from survey2report.dates import parse_date
from survey2report.repair import (
    drop_blank_rows,
    drop_duplicate_rows,
    drop_empty_columns,
    normalise_headers,
    normalise_values,
)

NUMERIC_THRESHOLD = 0.9
DATE_THRESHOLD = 0.9
MAX_CATEGORIES = 25
MAX_UNIQUE_RATIO = 0.2
HIGH_MISSINGNESS = 0.4

# Name hints settle the columns that value evidence cannot: identifiers such as
# "REG-2000" and prose columns both look numeric to a forgiving parser, while
# "feedback_date" must still be read as a date.
_DATE_NAME_RE = re.compile(r"date|_on$|_at$|_time$|timestamp")
_ID_RE = re.compile(r"(?:^|_)id$|_code$|_key$")
_FREETEXT_RE = re.compile(r"name|comment|note|feedback|verbatim|description|reason|text$")
DATE_NAME_MIN = 0.5


def load_csv(path: str | Path) -> pd.DataFrame:
    """Read a survey CSV as raw text so the cleaner sees the original mess.

    Args:
        path: CSV file to read.

    Returns:
        The file contents as all-string columns, with no NA inference.

    Raises:
        ValueError: If the file is neither UTF-8 nor Latin-1 decodable.
    """
    target = Path(path)
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(
                target,
                dtype=str,
                keep_default_na=False,
                encoding=encoding,
                engine="python",
                on_bad_lines="skip",
            )
        except UnicodeDecodeError:
            continue
    raise ValueError(f"could not decode {target} as utf-8 or latin-1")


def save_cleaned(df: pd.DataFrame, path: str | Path) -> Path:
    """Write a cleaned table to CSV, rendering dates as ISO strings.

    Args:
        df: Cleaned table.
        path: Destination file path.

    Returns:
        The path that was written.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    for name in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[name]):
            out[name] = out[name].dt.strftime("%Y-%m-%d").astype("string")
    out.to_csv(target, index=False, lineterminator="\n")
    return target


def detect_column_type(series: pd.Series, name: str = "") -> ColumnType:
    """Classify a column as numeric, date, categorical or free text.

    Name hints decide the columns that value evidence cannot, then whole-cell
    evidence decides the rest.

    Args:
        series: Column of raw values.
        name: Column name, used for identifier and free-text hints.

    Returns:
        The detected column type.
    """
    values = [value for value in series.tolist() if not is_missing(value)]
    if not values:
        return "text"
    numeric_ratio = _ratio(values, is_number_like)
    date_ratio = _ratio(values, lambda value: parse_date(value) is not None)
    if _DATE_NAME_RE.search(name) and date_ratio >= DATE_NAME_MIN:
        return "date"
    if _ID_RE.search(name) or _FREETEXT_RE.search(name):
        return "text"
    if date_ratio >= DATE_THRESHOLD:
        return "date"
    if numeric_ratio >= NUMERIC_THRESHOLD:
        return "numeric"
    unique = len({str(value) for value in values})
    if unique <= MAX_CATEGORIES or unique / len(values) <= MAX_UNIQUE_RATIO:
        return "categorical"
    return "text"


def _ratio(values: list[object], predicate: Callable[[object], bool]) -> float:
    """Return the share of values satisfying ``predicate``."""
    return sum(1 for value in values if predicate(value)) / len(values)


def clean_csv(path: str | Path) -> tuple[pd.DataFrame, CleaningLog]:
    """Load and clean one survey CSV.

    Args:
        path: CSV file to clean.

    Returns:
        The cleaned table and its cleaning log.
    """
    target = Path(path)
    return clean_dataframe(load_csv(target), filename=target.name)


def clean_dataframe(
    df: pd.DataFrame, filename: str = "<dataframe>"
) -> tuple[pd.DataFrame, CleaningLog]:
    """Clean a raw survey table and record every change.

    Args:
        df: Raw table, usually straight from :func:`load_csv`.
        filename: Name used in the cleaning log heading.

    Returns:
        The cleaned table and its cleaning log.
    """
    log = CleaningLog(filename=filename, rows_in=len(df), columns_in=df.shape[1])
    log.missing_before = _missing_ratio(df)

    work = normalise_headers(df, log)
    work = normalise_values(work, log)
    work = drop_blank_rows(work, log)
    work = drop_empty_columns(work, log)
    work = drop_duplicate_rows(work, log)

    cleaned: dict[str, pd.Series] = {}
    for name in work.columns:
        column_type = detect_column_type(work[name], name)
        log.types[name] = column_type
        cleaned[name] = COERCERS[column_type](work[name], name, log)
    result = pd.DataFrame(cleaned)

    log.rows_out = len(result)
    log.columns_out = result.shape[1]
    log.missing_after = _missing_ratio(result)
    _record_column_stats(result, log)
    return result, log


def _record_column_stats(df: pd.DataFrame, log: CleaningLog) -> None:
    """Store per-column counts and flag columns that are mostly missing."""
    for name in df.columns:
        missing = int(df[name].isna().sum())
        log.stats[name] = (int(df[name].nunique(dropna=True)), missing)
        ratio = missing / len(df) if len(df) else 0.0
        if ratio >= HIGH_MISSINGNESS:
            log.add(
                f"{ratio:.0%} missing after cleaning",
                "flagged low-confidence column",
                missing,
                column=name,
            )


def _missing_ratio(df: pd.DataFrame) -> float:
    """Return the share of cells that count as missing."""
    if df.empty or df.shape[1] == 0:
        return 0.0
    mask = df.apply(lambda column: column.map(is_missing))
    return float(mask.to_numpy().mean())


# ``parse_number`` stays re-exported here because reporting code reads it too.
__all__ = [
    "clean_csv",
    "clean_dataframe",
    "detect_column_type",
    "load_csv",
    "parse_number",
    "save_cleaned",
]
