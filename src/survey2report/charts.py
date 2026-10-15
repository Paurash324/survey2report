"""Chart generation: three to five slide-ready PNGs per dataset.

Every chart is drawn with the same restrained palette and saved headlessly, so
the reports look consistent without any display available.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from survey2report.stats import (
    AnalysisResult,
    CategorySummary,
    Correlation,
    DateSummary,
    NumericSummary,
    SegmentComparison,
)

ACCENT = "#3f6f9f"
SECONDARY = "#c98a3d"
MUTED = "#8b98a5"
GRID = "#dde3e8"
FIGSIZE = (9.0, 5.0)
DPI = 150
MAX_CHARTS = 5


@dataclass(slots=True)
class Chart:
    """A rendered chart file plus the caption that explains it."""

    title: str
    path: Path
    caption: str

    @property
    def filename(self) -> str:
        """Return the chart file name.

        Returns:
            The file name only, without directories.
        """
        return self.path.name


# Shared styling: one palette and one look for every chart in every report.
matplotlib.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.edgecolor": GRID,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def _new_figure() -> tuple[Figure, Axes]:
    """Create a slide-sized figure and axes without a GUI backend."""
    figure = Figure(figsize=FIGSIZE)
    return figure, figure.subplots()


def _finish(ax: Axes) -> None:
    """Remove chart junk and keep a light horizontal grid."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _save(fig: Figure, path: Path, title: str, caption: str) -> Chart:
    """Write a figure to disk."""
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    return Chart(title=title, path=path, caption=caption)


def _distribution(df: pd.DataFrame, summary: NumericSummary, path: Path) -> Chart:
    """Histogram of one measure, clipped to the 1st-99th percentile."""
    series = df[summary.column].dropna().astype("float64")
    fig, ax = _new_figure()
    bins = int(min(20, max(6, series.nunique())))
    ax.hist(series, bins=bins, color=ACCENT, edgecolor="white")
    ax.axvline(summary.median, color=SECONDARY, linestyle="--", linewidth=2,
               label=f"median {summary.median:.1f}")
    ax.axvline(summary.mean, color=MUTED, linestyle=":", linewidth=2,
               label=f"mean {summary.mean:.1f}")
    low, high = (float(value) for value in series.quantile([0.01, 0.99]))
    if high > low:
        padding = 0.05 * (high - low)
        ax.set_xlim(low - padding, high + padding)
    ax.set_title(f"Distribution of {summary.column}")
    ax.set_xlabel(summary.column)
    ax.set_ylabel("Responses")
    ax.legend(frameon=False)
    _finish(ax)
    caption = (
        f"{summary.count} answers, median {summary.median:.1f} and mean {summary.mean:.1f}; "
        "the axis is clipped to the 1st-99th percentile so outliers cannot squash the shape."
    )
    return _save(fig, path, f"Distribution of {summary.column}", caption)


def _categories(summary: CategorySummary, path: Path) -> Chart:
    """Horizontal bar chart of one categorical column."""
    levels = [level for level, _ in summary.distribution][::-1]
    counts = [count for _, count in summary.distribution][::-1]
    fig, ax = _new_figure()
    ax.barh(levels, counts, color=ACCENT)
    for index, count in enumerate(counts):
        ax.text(count, index, f" {count}", va="center", color=MUTED, fontsize=9)
    ax.set_title(f"{summary.column} mix")
    ax.set_xlabel("Responses")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    caption = (
        f"{summary.unique} levels over {summary.count} answers; {summary.top} is the largest "
        f"group at {summary.top_share:.0%}."
    )
    return _save(fig, path, f"{summary.column} mix", caption)


def _segments(comparison: SegmentComparison, path: Path) -> Chart:
    """Column chart comparing one measure across one segment column."""
    levels = [level for level, _, _ in comparison.groups]
    means = [mean for _, mean, _ in comparison.groups]
    colors = [ACCENT if level == comparison.best else MUTED for level in levels]
    fig, ax = _new_figure()
    ax.bar(range(len(levels)), means, color=colors, width=0.6)
    for index, mean in enumerate(means):
        ax.text(index, mean, f"{mean:.1f}", ha="center", va="bottom", fontsize=9, color=MUTED)
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels(levels, rotation=20 if max(map(len, levels)) > 8 else 0, ha="right")
    ax.set_title(f"{comparison.measure} by {comparison.segment_column}")
    ax.set_ylabel(comparison.measure)
    _finish(ax)
    caption = (
        f"{comparison.best} averages {comparison.best_value:.1f} against "
        f"{comparison.worst} at {comparison.worst_value:.1f}, a {comparison.spread:.0%} gap."
    )
    return _save(fig, path, f"{comparison.measure} by {comparison.segment_column}", caption)


def _correlation(df: pd.DataFrame, correlation: Correlation, path: Path) -> Chart:
    """Scatter plot of the strongest correlation with a fitted line."""
    x = df[correlation.left].astype("float64")
    y = df[correlation.right].astype("float64")
    mask = x.notna() & y.notna()
    fig, ax = _new_figure()
    ax.scatter(x[mask], y[mask], color=ACCENT, alpha=0.65, s=28, edgecolor="white")
    if int(mask.sum()) >= 3:
        slope, intercept = np.polyfit(x[mask], y[mask], 1)
        xs = np.linspace(float(x[mask].min()), float(x[mask].max()), 50)
        ax.plot(xs, slope * xs + intercept, color=SECONDARY, linewidth=2)
    ax.set_title(f"{correlation.left} vs {correlation.right}")
    ax.set_xlabel(correlation.left)
    ax.set_ylabel(correlation.right)
    _finish(ax)
    caption = f"r = {correlation.value:+.2f}, a {correlation.strength} relationship."
    return _save(fig, path, f"{correlation.left} vs {correlation.right}", caption)


def _trend(summary: DateSummary, path: Path) -> Chart:
    """Monthly response counts for one date column."""
    labels = [period for period, _ in summary.monthly]
    counts = [count for _, count in summary.monthly]
    fig, ax = _new_figure()
    ax.bar(range(len(labels)), counts, color=ACCENT, width=0.6)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45 if len(labels) > 6 else 0, ha="right")
    ax.set_title(f"{summary.column} over time")
    ax.set_ylabel("Responses")
    _finish(ax)
    caption = (
        f"{summary.count} dated responses from {summary.earliest} to {summary.latest} "
        f"({summary.span_days} days)."
    )
    return _save(fig, path, f"{summary.column} over time", caption)


def build_charts(
    df: pd.DataFrame,
    result: AnalysisResult,
    out_dir: str | Path,
    max_charts: int = MAX_CHARTS,
) -> list[Chart]:
    """Render the charts that suit one dataset.

    Args:
        df: Cleaned table.
        result: Analysis result for the same table, which selects what to draw.
        out_dir: Directory that receives the PNG files.
        max_charts: Upper bound on how many charts to render.

    Returns:
        Rendered charts in slide order, with the strongest material first.
    """
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)

    plan: list[tuple[str, Callable[[Path], Chart]]] = []
    if result.numeric:
        plan.append(("distribution", lambda path: _distribution(df, result.numeric[0], path)))
    if result.categorical:
        plan.append(("categories", lambda path: _categories(result.categorical[0], path)))
    if result.segments:
        plan.append(("segments", lambda path: _segments(result.segments[0], path)))
    if result.correlations:
        plan.append(("correlation", lambda path: _correlation(df, result.correlations[0], path)))
    if result.dates:
        plan.append(("trend", lambda path: _trend(result.dates[0], path)))

    charts: list[Chart] = []
    for index, (slug, render) in enumerate(plan[:max_charts], start=1):
        charts.append(render(target / f"{index:02d}_{slug}.png"))
    return charts
