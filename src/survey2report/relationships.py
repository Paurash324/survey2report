"""Correlations between measures and comparisons across segments."""

from __future__ import annotations

import pandas as pd

from survey2report.cleaninglog import ColumnType
from survey2report.stats import Correlation, SegmentComparison

MIN_GROUP_SIZE = 5
MIN_SPREAD = 0.1
MAX_SEGMENT_LEVELS = 8
MAX_MEASURES = 3
MIN_ABS_CORRELATION = 0.3
TOP_CORRELATIONS = 5
TOP_SEGMENTS = 4


def strength_label(value: float) -> str:
    """Describe a correlation coefficient in words.

    Args:
        value: Pearson correlation coefficient.

    Returns:
        A phrase such as ``"moderate positive"``.
    """
    magnitude = abs(value)
    if magnitude >= 0.7:
        band = "strong"
    elif magnitude >= 0.5:
        band = "moderate"
    elif magnitude >= 0.3:
        band = "weak"
    else:
        band = "negligible"
    return f"{band} {'positive' if value >= 0 else 'negative'}"


def correlations(
    df: pd.DataFrame, types: dict[str, ColumnType], top: int = TOP_CORRELATIONS
) -> list[Correlation]:
    """Find the strongest linear relationships between numeric columns.

    Args:
        df: Cleaned table.
        types: Detected column types.
        top: Maximum number of pairs to return.

    Returns:
        Correlations sorted by absolute strength.
    """
    candidates = [
        name
        for name, column_type in types.items()
        if column_type == "numeric" and df[name].nunique(dropna=True) > 1
    ]
    if len(candidates) < 2:
        return []
    matrix = df[candidates].corr(numeric_only=True)
    pairs: list[Correlation] = []
    for index, left in enumerate(candidates):
        for right in candidates[index + 1 :]:
            value = matrix.loc[left, right]
            if pd.notna(value) and abs(value) >= MIN_ABS_CORRELATION:
                pairs.append(
                    Correlation(
                        left=left,
                        right=right,
                        value=float(value),
                        strength=strength_label(float(value)),
                    )
                )
    pairs.sort(key=lambda pair: abs(pair.value), reverse=True)
    return pairs[:top]


def pick_measures(df: pd.DataFrame, types: dict[str, ColumnType]) -> list[str]:
    """Choose the most informative numeric measures to compare across segments.

    Args:
        df: Cleaned table.
        types: Detected column types.

    Returns:
        Up to ``MAX_MEASURES`` column names, most variable first.
    """
    scored: list[tuple[float, str]] = []
    for name, column_type in types.items():
        if column_type != "numeric":
            continue
        series = df[name].dropna()
        if series.size < MIN_GROUP_SIZE or series.nunique() < 2:
            continue
        mean = abs(float(series.mean()))
        variation = float(series.std(ddof=1)) / mean if mean else 0.0
        scored.append((variation, name))
    scored.sort(reverse=True)
    return [name for _, name in scored[:MAX_MEASURES]]


def segment_comparisons(
    df: pd.DataFrame, types: dict[str, ColumnType], top: int = TOP_SEGMENTS
) -> list[SegmentComparison]:
    """Compare the chosen measures across categorical segments.

    Args:
        df: Cleaned table.
        types: Detected column types.
        top: Maximum number of comparisons, at most one per measure.

    Returns:
        Comparisons ordered by the relative gap between best and worst segment,
        ignoring gaps smaller than ``MIN_SPREAD``.
    """
    segment_columns = [
        name
        for name, column_type in types.items()
        if column_type == "categorical" and 2 <= df[name].nunique(dropna=True) <= MAX_SEGMENT_LEVELS
    ]
    if not segment_columns:
        return []

    candidates: list[SegmentComparison] = []
    for measure in pick_measures(df, types):
        overall = abs(float(df[measure].mean()))
        for segment in segment_columns:
            grouped = df.groupby(segment, observed=True)[measure].agg(["mean", "count"]).dropna()
            grouped = grouped[grouped["count"] >= MIN_GROUP_SIZE]
            if len(grouped) < 2:
                continue
            gap = float(grouped["mean"].max() - grouped["mean"].min())
            if not overall or gap / overall < MIN_SPREAD:
                continue
            candidates.append(
                SegmentComparison(
                    segment_column=segment,
                    measure=measure,
                    groups=[
                        (str(level), float(row["mean"]), int(row["count"]))
                        for level, row in grouped.iterrows()
                    ],
                    spread=gap / overall if overall else 0.0,
                    best=str(grouped["mean"].idxmax()),
                    worst=str(grouped["mean"].idxmin()),
                    best_value=float(grouped["mean"].max()),
                    worst_value=float(grouped["mean"].min()),
                )
            )

    candidates.sort(key=lambda comparison: comparison.spread, reverse=True)
    chosen: list[SegmentComparison] = []
    used: set[str] = set()
    for candidate in candidates:
        if candidate.measure in used:
            continue
        used.add(candidate.measure)
        chosen.append(candidate)
        if len(chosen) == top:
            break
    return chosen
