"""Run one survey CSV through the whole pipeline and write its output folder."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from survey2report.analyzer import analyze
from survey2report.charts import MAX_CHARTS, Chart, build_charts
from survey2report.cleaner import clean_csv, save_cleaned
from survey2report.report import build_report

CLEANED_NAME = "cleaned.csv"
CLEANING_LOG_NAME = "cleaning_log.md"
ANALYSIS_NAME = "analysis.md"
REPORT_NAME = "report.pptx"
CHARTS_DIRNAME = "charts"


@dataclass(slots=True)
class DatasetOutput:
    """Everything produced for one input CSV.

    Attributes:
        source: Input CSV that was processed.
        directory: Output folder holding every artefact.
        rows: Cleaned row count.
        columns: Cleaned column count.
        findings: Key findings shown on the report's findings slide.
        charts: Rendered charts, in slide order.
        report: Path of the generated .pptx file.
    """

    source: Path
    directory: Path
    rows: int
    columns: int
    findings: list[str] = field(default_factory=list)
    charts: list[Chart] = field(default_factory=list)
    report: Path = Path()

    @property
    def artifacts(self) -> list[Path]:
        """List the files written for this dataset.

        Returns:
            The report, cleaned data, logs and charts.
        """
        return [self.report, *[chart.path for chart in self.charts]]


def discover_csvs(input_dir: str | Path) -> list[Path]:
    """Find the survey CSVs in a folder.

    Args:
        input_dir: Folder to scan.

    Returns:
        CSV paths sorted by name, ignoring hidden and temporary files.
    """
    folder = Path(input_dir)
    if not folder.is_dir():
        return []
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() == ".csv" and not path.name.startswith(("~", "."))
    )


def process_dataset(
    csv_path: str | Path, output_root: str | Path, max_charts: int = MAX_CHARTS
) -> DatasetOutput:
    """Clean, analyse, chart and report one CSV into ``output_root/<stem>/``.

    Args:
        csv_path: Survey CSV to process.
        output_root: Folder that receives one sub-folder per dataset.
        max_charts: Upper bound on charts per dataset.

    Returns:
        A description of everything that was written.
    """
    source = Path(csv_path)
    directory = Path(output_root) / source.stem
    directory.mkdir(parents=True, exist_ok=True)

    clean, log = clean_csv(source)
    result = analyze(clean, log)
    charts = build_charts(clean, result, directory / CHARTS_DIRNAME, max_charts=max_charts)

    save_cleaned(clean, directory / CLEANED_NAME)
    log.write(directory / CLEANING_LOG_NAME)
    (directory / ANALYSIS_NAME).write_text(result.to_markdown(), encoding="utf-8")
    report = build_report(result, charts, log, directory / REPORT_NAME)

    return DatasetOutput(
        source=source,
        directory=directory,
        rows=result.rows,
        columns=result.column_count,
        findings=result.findings,
        charts=charts,
        report=report,
    )
