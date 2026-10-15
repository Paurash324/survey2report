"""Per-column descriptive statistics for a cleaned survey table."""

from __future__ import annotations

import pandas as pd

from survey2report.cleaninglog import ColumnType
from survey2report.stats import CategorySummary, DateSummary, NumericSummary

MAX_CATEGORY_LEVELS = 12


def numeric_summaries(df: pd.DataFrame, types: dict[str, ColumnType]) -> list[NumericSummary]:
    """Summarise every numeric column.

    Args:
        df: Cleaned table.
        types: Detected column types.

    Returns:
        One summary per numeric column that holds data.
    """
    out: list[NumericSummary] = []
    for name, column_type in types.items():
        if column_type != "numeric":
            continue
        series = df[name].dropna()
        if series.empty:
            continue
        q1, q3 = (float(value) for value in series.quantile([0.25, 0.75]))
        iqr = q3 - q1
        extreme = ((series < q1 - 3 * iqr) | (series > q3 + 3 * iqr)) if iqr > 0 else None
        out.append(
            NumericSummary(
                column=name,
                count=int(series.size),
                missing=int(df[name].isna().sum()),
                mean=float(series.mean()),
                median=float(series.median()),
                std=float(series.std(ddof=1)) if series.size > 1 else 0.0,
                minimum=float(series.min()),
                maximum=float(series.max()),
                q1=q1,
                q3=q3,
                outliers=int(extreme.sum()) if extreme is not None else 0,
            )
        )
    return out


def category_summaries(df: pd.DataFrame, types: dict[str, ColumnType]) -> list[CategorySummary]:
    """Summarise every categorical column.

    Args:
        df: Cleaned table.
        types: Detected column types.

    Returns:
        One summary per categorical column with a usable number of levels.
    """
    out: list[CategorySummary] = []
    for name, column_type in types.items():
        if column_type != "categorical":
            continue
        counts = df[name].dropna().value_counts()
        if counts.empty or counts.size > MAX_CATEGORY_LEVELS:
            continue
        out.append(
            CategorySummary(
                column=name,
                count=int(counts.sum()),
                unique=int(counts.size),
                top=str(counts.index[0]),
                top_share=float(counts.iloc[0] / counts.sum()),
                distribution=[(str(level), int(value)) for level, value in counts.items()],
            )
        )
    return out


def date_summaries(df: pd.DataFrame, types: dict[str, ColumnType]) -> list[DateSummary]:
    """Summarise every date column, including its monthly counts.

    Args:
        df: Cleaned table.
        types: Detected column types.

    Returns:
        One summary per date column that holds data.
    """
    out: list[DateSummary] = []
    for name, column_type in types.items():
        if column_type != "date":
            continue
        series = pd.to_datetime(df[name]).dropna()
        if series.empty:
            continue
        monthly = series.dt.to_period("M").value_counts().sort_index()
        out.append(
            DateSummary(
                column=name,
                count=int(series.size),
                earliest=series.min().strftime("%Y-%m-%d"),
                latest=series.max().strftime("%Y-%m-%d"),
                span_days=int((series.max() - series.min()).days),
                monthly=[(str(period), int(count)) for period, count in monthly.items()],
            )
        )
    return out
