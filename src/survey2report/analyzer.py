"""Orchestrate the analysis and turn it into report-ready key findings.

The statistics themselves live in :mod:`survey2report.summaries` and
:mod:`survey2report.relationships`; this module wires them together and
re-exports them so callers have a single entry point.
"""

from __future__ import annotations

import pandas as pd

from survey2report.cleaninglog import CleaningLog
from survey2report.relationships import (
    MAX_MEASURES,
    MAX_SEGMENT_LEVELS,
    MIN_ABS_CORRELATION,
    MIN_GROUP_SIZE,
    TOP_CORRELATIONS,
    TOP_SEGMENTS,
    correlations,
    pick_measures,
    segment_comparisons,
    strength_label,
)
from survey2report.stats import AnalysisResult
from survey2report.summaries import (
    MAX_CATEGORY_LEVELS,
    category_summaries,
    date_summaries,
    numeric_summaries,
)

MAX_FINDINGS = 6

# Answers that carry no signal should not become a headline finding.
NON_ANSWERS = {"unknown", "not sure", "prefer not to say", "no answer"}

__all__ = [
    "MAX_CATEGORY_LEVELS",
    "NON_ANSWERS",
    "MAX_FINDINGS",
    "MAX_MEASURES",
    "MAX_SEGMENT_LEVELS",
    "MIN_ABS_CORRELATION",
    "MIN_GROUP_SIZE",
    "TOP_CORRELATIONS",
    "TOP_SEGMENTS",
    "analyze",
    "category_summaries",
    "correlations",
    "date_summaries",
    "key_findings",
    "numeric_summaries",
    "pick_measures",
    "segment_comparisons",
    "strength_label",
]


def analyze(df: pd.DataFrame, log: CleaningLog) -> AnalysisResult:
    """Compute every analysis artefact for one cleaned dataset.

    Args:
        df: Cleaned table.
        log: Cleaning log for the same table, providing column types.

    Returns:
        The analysis result, including report-ready key findings.
    """
    result = AnalysisResult(filename=log.filename, rows=len(df))
    result.numeric = numeric_summaries(df, log.types)
    result.categorical = category_summaries(df, log.types)
    result.dates = date_summaries(df, log.types)
    result.correlations = correlations(df, log.types)
    result.segments = segment_comparisons(df, log.types)
    result.findings = key_findings(result, log)
    return result


def key_findings(result: AnalysisResult, log: CleaningLog | None = None) -> list[str]:
    """Turn the analysis into short, human-readable findings.

    Args:
        result: Computed analysis.
        log: Optional cleaning log, used for data-quality context.

    Returns:
        Up to ``MAX_FINDINGS`` bullet strings, most important first.
    """
    findings = [f"{result.rows} responses across {result.column_count} analysed columns"]
    if result.categorical:
        informative = [
            summary for summary in result.categorical if summary.top.lower() not in NON_ANSWERS
        ] or result.categorical
        top = max(informative, key=lambda summary: summary.top_share)
        findings.append(f"Most common {top.column}: {top.top} ({top.top_share:.0%} of responses)")
    if result.correlations:
        strongest = result.correlations[0]
        findings.append(
            f"Strongest relationship: {strongest.label} (r = {strongest.value:+.2f}, "
            f"{strongest.strength})"
        )
    for comparison in result.segments[:2]:
        findings.append(
            f"Highest {comparison.measure} by {comparison.segment_column}: "
            f"{comparison.best} ({comparison.best_value:.1f}) vs "
            f"{comparison.worst} ({comparison.worst_value:.1f})"
        )
    noisy = [summary for summary in result.numeric if summary.outliers]
    if noisy:
        worst = max(noisy, key=lambda summary: summary.outliers)
        findings.append(f"{worst.outliers} extreme values in {worst.column} worth verifying")
    if log is not None and log.duplicates_removed:
        findings.append(f"{log.duplicates_removed} duplicate rows were removed during cleaning")
    return findings[:MAX_FINDINGS]
