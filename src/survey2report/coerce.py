"""Forgiving coercion primitives for messy survey cells.

Survey exports mix currency symbols, trailing units, thousands separators,
comma decimals and sentinel placeholders inside a single column, so these
helpers must survive input that no type annotation fully describes.
"""

from __future__ import annotations

import re

import pandas as pd

MISSING_SENTINELS: frozenset[str] = frozenset(
    {"", "-", "--", "?", ".", "n/a", "na", "null", "nil", "none", "nan", "missing", "unknown?"}
)

# Binary answers arrive as Y/N, yes/no and 1/0 in the same column. Columns of
# pure 1/0 are detected as numeric, so this only ever sees answered categories.
SYNONYMS: dict[str, str] = {
    "y": "Yes",
    "yes": "Yes",
    "1": "Yes",
    "true": "Yes",
    "n": "No",
    "no": "No",
    "0": "No",
    "false": "No",
}

_CURRENCY_RE = re.compile(r"(?i)\b(?:usd|eur|gbp|inr)\b|[$€£₹]")
# A sign only counts at a word boundary, so "REG-2000" reads as 2000 rather
# than as the negative number -2000.
_NUMBER_RE = re.compile(r"(?<![\w.])[-+]?\d[\d.,]*")
_PLAIN_NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")
_WHITESPACE_RE = re.compile(r"\s+")

# Whole-cell numeric test used for type detection: the number must lead the cell
# and anything left over may only be decoration (currency, unit, "9/10",
# "3 - Agree"). "REG-2000", "Option 1" and "2024-01-05" therefore never look
# numeric, while "45 min" and "$1,299.00" do.
_NUMBER_LIKE_RE = re.compile(
    r"""^
    [\s$€£₹]*
    (?:usd|eur|gbp|inr)?
    [\s$€£₹]*
    [-+]?\d[\d.,]*
    (?:
        \s*%
      | \s*(?:
            min|mins|minute|minutes|hours?|hrs?|years?|yrs?|days?|weeks?|months?|kg|cm|points?|pts?
        )s?\b
      | \s*/\s*\d+
      | \s+out\s+of\s+\d+
      | \s*[-–]\s*[A-Za-z][A-Za-z\s]*
    )?
    \s*$""",
    re.IGNORECASE | re.VERBOSE,
)


def normalise_header(name: str) -> str:
    """Convert a raw CSV header into a snake_case identifier.

    Args:
        name: Header exactly as it appears in the file.

    Returns:
        A lowercase ``snake_case`` name, never empty.
    """
    snake = _WHITESPACE_RE.sub(" ", str(name)).strip().lower()
    return re.sub(r"[^0-9a-z]+", "_", snake).strip("_") or "column"


def is_missing(value: object) -> bool:
    """Report whether a raw cell should be treated as missing.

    Args:
        value: Any cell value.

    Returns:
        True for nulls and for the usual survey sentinels such as ``"N/A"``.
    """
    if value is None or value is pd.NA:
        return True
    if isinstance(value, float) and value != value:  # NaN without importing numpy
        return True
    return str(value).strip().lower() in MISSING_SENTINELS


def clean_text(value: object) -> str | None:
    """Strip padding and collapse internal whitespace in a cell.

    Args:
        value: Any cell value.

    Returns:
        The tidied text, or None when the cell counts as missing.
    """
    if is_missing(value):
        return None
    return _WHITESPACE_RE.sub(" ", str(value)).strip()


def parse_number(value: object) -> float | None:
    """Extract a number from a messy cell such as ``"$1,299.00"`` or ``"45 min"``.

    Args:
        value: Any cell value.

    Returns:
        The parsed float, or None when no number can be found.
    """
    text = clean_text(value)
    if text is None:
        return None
    match = _NUMBER_RE.search(_CURRENCY_RE.sub("", text).replace("%", ""))
    if match is None:
        return None
    try:
        return float(_resolve_separators(match.group(0).rstrip(".,")))
    except ValueError:
        return None


def _resolve_separators(token: str) -> str:
    """Turn thousand separators and comma decimals into a plain float literal."""
    if "," not in token:
        return token
    if token.count(",") > 1 or "." in token:
        return token.replace(",", "")
    head, _, tail = token.partition(",")
    is_thousands = len(tail) == 3 and tail.isdigit() and head.lstrip("+-").isdigit() and head != "0"
    return head + tail if is_thousands else f"{head}.{tail}"


def is_number_like(value: object) -> bool:
    """Report whether a whole cell is a number plus decoration only.

    This strict counterpart of :func:`parse_number` drives type detection, so
    identifiers such as ``"REG-2000"`` and prose such as ``"Option 1"`` are not
    mistaken for measurements.

    Args:
        value: Any cell value.

    Returns:
        True when the cell reads as a single number with optional decoration.
    """
    text = clean_text(value)
    return bool(text and _NUMBER_LIKE_RE.match(text))


def is_plain_number(value: object) -> bool:
    """Report whether a cell is already a clean number, e.g. ``"3"`` or ``"2.5"``.

    Args:
        value: Any cell value.

    Returns:
        True when no coercion is needed.
    """
    text = clean_text(value)
    return bool(text and _PLAIN_NUMBER_RE.fullmatch(text))


def _preferred_label(values: pd.Series) -> str:
    """Pick the spelling to keep for one set of label variants."""
    counts = values.value_counts()
    most_common = counts[counts == counts.max()].index
    if len(most_common) == 1:
        return str(most_common[0])

    # Deterministic tie-break, preferring "Yes" over "yes"/"YES" and "SaaS"
    # over "saas".
    def rank(label: object) -> tuple[bool, int, str]:
        text = str(label)
        return (text == text.capitalize(), sum(char.isupper() for char in text), text)

    return max(most_common, key=rank)


def canonical_labels(series: pd.Series) -> pd.Series:
    """Collapse casing, padding and spelling variants of a categorical column.

    Synonym answers such as ``Y``, ``yes`` and ``1`` collapse into one label;
    every other variant keeps its most common spelling.

    Args:
        series: Column of raw text values.

    Returns:
        The column with one canonical label per group of variants.
    """
    text = series.astype("string").str.strip()
    present = text.dropna()
    if present.empty:
        return text
    preferred = present.groupby(present.str.lower()).agg(_preferred_label)
    targets = {
        str(key): SYNONYMS.get(str(key), str(value))
        for key, value in preferred.items()
    }
    return text.str.lower().map(targets).astype("string")


def count_variant_groups(series: pd.Series) -> int:
    """Count labels that appear with more than one spelling.

    Args:
        series: Column of raw text values.

    Returns:
        Number of labels that had spelling variants.
    """
    text = series.astype("string").str.strip().dropna()
    if text.empty:
        return 0
    return int((text.groupby(text.str.lower()).nunique() > 1).sum())
