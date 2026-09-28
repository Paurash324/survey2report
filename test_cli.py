"""Tests for the CLI and the per-dataset pipeline."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from pptx import Presentation

from survey2report import cli
from survey2report.pipeline import discover_csvs, process_dataset

SAMPLE = "employee_engagement_2024.csv"


@pytest.fixture
def input_dir(tmp_path: Path, examples_dir: Path) -> Path:
    folder = tmp_path / "in"
    folder.mkdir()
    shutil.copy(examples_dir / SAMPLE, folder)
    return folder


def test_discover_csvs_ignores_other_files(tmp_path: Path) -> None:
    (tmp_path / "a.csv").write_text("x\n1\n", encoding="utf-8")
    (tmp_path / "B.CSV").write_text("x\n1\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore me\n", encoding="utf-8")
    (tmp_path / "~temp.csv").write_text("x\n1\n", encoding="utf-8")

    # Path ordering is case-insensitive on Windows, so only compare the contents.
    assert {path.name for path in discover_csvs(tmp_path)} == {"a.csv", "B.CSV"}
    assert discover_csvs(tmp_path / "missing") == []


def test_process_dataset_writes_every_artifact(input_dir: Path, tmp_path: Path) -> None:
    output = process_dataset(input_dir / SAMPLE, tmp_path / "out")

    assert output.rows == 180
    assert 3 <= len(output.charts) <= 5
    assert output.findings
    assert output.directory == tmp_path / "out" / "employee_engagement_2024"

    for name in ("report.pptx", "cleaned.csv", "cleaning_log.md", "analysis.md"):
        assert (output.directory / name).stat().st_size > 0
    assert len(list((output.directory / "charts").glob("*.png"))) == len(output.charts)
    assert set(output.artifacts) <= set(output.directory.rglob("*"))


def test_process_dataset_respects_max_charts(input_dir: Path, tmp_path: Path) -> None:
    output = process_dataset(input_dir / SAMPLE, tmp_path / "out", max_charts=3)
    assert len(output.charts) == 3


def test_main_reports_progress_and_returns_zero(
    input_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = cli.main(["--input", str(input_dir), "--output", str(tmp_path / "out")])
    captured = capsys.readouterr()

    assert code == 0
    assert "survey2report 0.1.0: 1 dataset(s)" in captured.out
    assert f"{SAMPLE}: 180 rows, 5 charts" in captured.out
    assert "done: 1/1 report(s) written" in captured.out
    assert captured.err == ""

    deck = Presentation(str(tmp_path / "out" / "employee_engagement_2024" / "report.pptx"))
    assert len(deck.slides) == 11


def test_main_honours_max_charts(input_dir: Path, tmp_path: Path) -> None:
    assert cli.main(["--input", str(input_dir), "--output", str(tmp_path / "out"), "-c", "3"]) == 0
    charts = list((tmp_path / "out" / "employee_engagement_2024" / "charts").glob("*.png"))
    assert len(charts) == 3


def test_one_broken_file_does_not_stop_the_run(
    tmp_path: Path,
    examples_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    folder = tmp_path / "in"
    folder.mkdir()
    shutil.copy(examples_dir / SAMPLE, folder)
    (folder / "broken.csv").write_text("a,b\n1,2\n", encoding="utf-8")

    real = cli.process_dataset

    def flaky(path: str | Path, output_root: str | Path, max_charts: int = 5) -> object:
        if Path(path).stem == "broken":
            raise ValueError("unreadable table")
        return real(path, output_root, max_charts=max_charts)

    monkeypatch.setattr(cli, "process_dataset", flaky)
    code = cli.main(["--input", str(folder), "--output", str(tmp_path / "out")])
    captured = capsys.readouterr()

    assert code == 1
    assert "FAILED broken.csv: unreadable table" in captured.err
    assert "done: 1/2 report(s) written" in captured.out
