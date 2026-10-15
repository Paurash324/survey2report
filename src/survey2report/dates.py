"""Date parsing helpers for the several layouts found in survey exports."""

from __future__ import annotations

import re
from datetime import datetime

import pandas as pd

from survey2report.coerce import clean_text

# Day-first formats are tried before month-first, so an ambiguous "05/03/2024"
# is read as 5 March. Columns holding only unambiguous month-first values still
# parse correctly, because the earlier formats simply fail.
DATE_FORMATS: tuple[str, ...] = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%b-%Y",
    "%d-%B-%Y",
    "%b %d, %Y",
    "%B %d, %Y",
    "%d.%m.%Y",
)

_SLASH_DATE_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_date(value: object) -> datetime | None:
    """Parse a date written in any of the supported survey layouts.

    Args:
        value: Any cell value.

    Returns:
        The parsed datetime, or None when no known format matches.
    """
    text = clean_text(value)
    if text is None:
        return None
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(text, date_format)
        except ValueError:
            continue
    return None


def is_iso_date(value: object) -> bool:
    """Report whether a cell is already an ISO ``YYYY-MM-DD`` date.

    Args:
        value: Any cell value.

    Returns:
        True when the cell needs no date normalisation.
    """
    text = clean_text(value)
    return bool(text and _ISO_DATE_RE.fullmatch(text))


def count_slash_dates(series: pd.Series) -> int:
    """Count cells whose date uses an ambiguous ``DD/MM/YYYY``-style layout.

    Args:
        series: Column of raw text values.

    Returns:
        Number of cells matching a slash-separated date layout.
    """
    text = series.dropna().astype("string")
    return int(text.str.match(_SLASH_DATE_RE).sum())
