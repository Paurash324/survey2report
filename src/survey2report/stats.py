"""Typed containers for everything the analyzer computes, and their rendering."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class NumericSummary:
    """Summary statistics for one numeric column."""

    column: str
    count: int
    missing: int
    mean: float
    median: float
    std: float
    minimum: float
    maximum: float
    q1: float
    q3: float
    outliers: int

    @property
    def spread(self) -> float:
        """Return the distance between the smallest and largest value.

        Returns:
            The observed range.
        """
        return self.maximum - self.minimum

    @property
    def iqr(self) -> float:
        """Return the interquartile range.

        Returns:
            The interquartile range.
        """
        return self.q3 - self.q1


@dataclass(slots=True)
class CategorySummary:
    """Frequency summary for one categorical column."""

    column: str
    count: int
    unique: int
    top: str
    top_share: float
    distribution: list[tuple[str, int]]


@dataclass(slots=True)
class DateSummary:
    """Coverage summary for one date column."""

    column: str
    count: int
    earliest: str
    latest: str
    span_days: int
    monthly: list[tuple[str, int]]


@dataclass(slots=True)
class Correlation:
    """A pairwise correlation between two numeric columns."""

    left: str
    right: str
    value: float
    strength: str

    @property
    def label(self) -> str:
        """Return a readable name for the pair.

        Returns:
            Both column names joined by an arrow.
        """
        return f"{self.left} ↔ {self.right}"


@dataclass(slots=True)
class SegmentComparison:
    """One measure compared across the levels of one segment column."""

    segment_column: str
    measure: str
    groups: list[tuple[str, float, int]]
    spread: float
    best: str
    worst: str
    best_value: float
    worst_value: float


@dataclass(slots=True)
class AnalysisResult:
    """Everything computed for one cleaned dataset."""

    filename: str
    rows: int
    numeric: list[NumericSummary] = field(default_factory=list)
    categorical: list[CategorySummary] = field(default_factory=list)
    dates: list[DateSummary] = field(default_factory=list)
    correlations: list[Correlation] = field(default_factory=list)
    segments: list[SegmentComparison] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)

    @property
    def measures(self) -> list[str]:
        """List the numeric columns that were summarised.

        Returns:
            Numeric column names.
        """
        return [summary.column for summary in self.numeric]

    @property
    def column_count(self) -> int:
        """Return how many columns were analysed.

        Returns:
            The number of typed columns.
        """
        return len(self.numeric) + len(self.categorical) + len(self.dates)

    def to_markdown(self) -> str:
        """Render the analysis as markdown.

        Returns:
            Markdown text with one section per result kind.
        """
        lines = [
            f"# Analysis — {self.filename}",
            "",
            f"- Rows analysed: **{self.rows}**",
            f"- Columns analysed: **{self.column_count}** "
            f"({len(self.numeric)} numeric, {len(self.categorical)} categorical, "
            f"{len(self.dates)} date)",
            "",
            "## Key findings",
            "",
        ]
        lines += [f"- {finding}" for finding in self.findings] or ["- No findings."]
        lines += [
            "",
            "## Numeric columns",
            "",
            "| Column | N | Missing | Mean | Median | Std | Min | Max |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        lines += [
            f"| `{s.column}` | {s.count} | {s.missing} | {s.mean:.2f} | {s.median:.2f} | "
            f"{s.std:.2f} | {s.minimum:.2f} | {s.maximum:.2f} |"
            for s in self.numeric
        ]
        lines += [
            "",
            "## Categorical columns",
            "",
            "| Column | Levels | Most common | Share |",
            "| --- | --- | --- | --- |",
        ]
        lines += [
            f"| `{s.column}` | {s.unique} | {s.top} | {s.top_share:.0%} |" for s in self.categorical
        ]
        lines += ["", "## Correlations", "", "| Pair | r | Strength |", "| --- | --- | --- |"]
        lines += [f"| {c.label} | {c.value:+.2f} | {c.strength} |" for c in self.correlations]
        if not self.correlations:
            lines.append("| — | — | none above threshold |")
        lines += [
            "",
            "## Segment comparisons",
            "",
            "| Segment | Measure | Best | Worst | Gap |",
            "| --- | --- | --- | --- | --- |",
        ]
        lines += [
            f"| `{s.segment_column}` | `{s.measure}` | {s.best} ({s.best_value:.1f}) | "
            f"{s.worst} ({s.worst_value:.1f}) | {s.spread:.0%} |"
            for s in self.segments
        ]
        if not self.segments:
            lines.append("| — | — | — | — | not enough data |")
        return "\n".join(lines) + "\n"
