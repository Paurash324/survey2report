"""Structured record of every cleaning action, and its markdown rendering."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

ColumnType = Literal["numeric", "categorical", "date", "text"]


@dataclass(slots=True)
class LogEntry:
    """A single recorded cleaning action.

    Attributes:
        issue: What was wrong, phrased for a non-technical reader.
        action: What the cleaner did about it.
        count: How many values, rows or columns were touched.
        column: Affected column, or None when the action spans the table.
        detail: Optional extra context such as renamed examples.
    """

    issue: str
    action: str
    count: int
    column: str | None = None
    detail: str = ""

    def to_row(self) -> str:
        """Render the entry as a markdown table row.

        Returns:
            A markdown table row with four cells.
        """
        column = f"`{self.column}`" if self.column else "—"
        detail = f" ({self.detail})" if self.detail else ""
        return f"| {column} | {self.issue} | {self.action}{detail} | {self.count} |"


@dataclass(slots=True)
class CleaningLog:
    """Everything the cleaner changed for one dataset, plus its rationale.

    Attributes:
        filename: Name of the source file the log describes.
        rows_in: Row count before cleaning.
        rows_out: Row count after cleaning.
        columns_in: Column count before cleaning.
        columns_out: Column count after cleaning.
        missing_before: Share of cells treated as missing in the raw file.
        missing_after: Share of missing cells in the cleaned table.
        duplicates_removed: Number of exact duplicate rows dropped.
        types: Detected type for every surviving column.
        stats: ``(unique, missing)`` counts per surviving column.
        entries: Ordered list of recorded actions.
    """

    filename: str
    rows_in: int = 0
    rows_out: int = 0
    columns_in: int = 0
    columns_out: int = 0
    missing_before: float = 0.0
    missing_after: float = 0.0
    duplicates_removed: int = 0
    types: dict[str, ColumnType] = field(default_factory=dict)
    stats: dict[str, tuple[int, int]] = field(default_factory=dict)
    entries: list[LogEntry] = field(default_factory=list)

    def add(
        self,
        issue: str,
        action: str,
        count: int,
        column: str | None = None,
        detail: str = "",
    ) -> None:
        """Record one cleaning action.

        Args:
            issue: What was wrong.
            action: What the cleaner did.
            count: Number of affected values, rows or columns.
            column: Affected column, if the action is column-scoped.
            detail: Optional extra context.
        """
        self.entries.append(
            LogEntry(issue=issue, action=action, count=count, column=column, detail=detail)
        )

    @property
    def type_counts(self) -> dict[str, int]:
        """Count how many columns of each type were detected.

        Returns:
            Mapping of column type to number of columns.
        """
        return dict(Counter(self.types.values()))

    def issues(self) -> list[str]:
        """List the distinct problems that the cleaner encountered.

        Returns:
            Issue descriptions, in first-seen order.
        """
        return list(dict.fromkeys(entry.issue for entry in self.entries))

    def quality_summary(self) -> list[str]:
        """Summarise data quality in report-ready bullets.

        Returns:
            Up to five short bullet strings.
        """
        removed = self.rows_in - self.rows_out
        bullets = [
            f"{self.rows_in} raw rows became {self.rows_out} analysis-ready rows "
            f"({removed} dropped)",
            f"{self.missing_before:.1%} of cells arrived missing; "
            f"{self.missing_after:.1%} remain after cleaning",
        ]
        if self.duplicates_removed:
            bullets.append(f"{self.duplicates_removed} exact duplicate rows were removed")
        if self.types:
            counts = ", ".join(f"{n} {name}" for name, n in sorted(self.type_counts.items()))
            bullets.append(f"Columns typed as {counts}")
        issues = self.issues()
        if issues:
            bullets.append("Repairs applied: " + "; ".join(issues[:4]))
        return bullets

    def to_markdown(self) -> str:
        """Render the whole log as markdown.

        Returns:
            Markdown text describing the run.
        """
        lines = [
            f"# Cleaning log — {self.filename}",
            "",
            f"- Rows: **{self.rows_in} → {self.rows_out}** "
            f"({self.rows_in - self.rows_out} removed)",
            f"- Columns: **{self.columns_in} → {self.columns_out}**",
            f"- Missing cells: **{self.missing_before:.1%} → {self.missing_after:.1%}**",
            f"- Recorded actions: **{len(self.entries)}**",
            "",
            "## Detected column types",
            "",
            "| Column | Type | Unique | Missing |",
            "| --- | --- | --- | --- |",
        ]
        for name, column_type in self.types.items():
            unique, missing = self.stats.get(name, (0, 0))
            lines.append(f"| `{name}` | {column_type} | {unique} | {missing} |")
        lines += [
            "",
            "## Actions taken",
            "",
            "| Column | Issue | Action | Cells |",
            "| --- | --- | --- | --- |",
        ]
        rows = [entry.to_row() for entry in self.entries]
        lines += rows if rows else ["| — | none | no repairs needed | 0 |"]
        return "\n".join(lines) + "\n"

    def write(self, path: str | Path) -> Path:
        """Write the markdown log to disk.

        Args:
            path: Destination file path.

        Returns:
            The path that was written.
        """
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.to_markdown(), encoding="utf-8")
        return target
