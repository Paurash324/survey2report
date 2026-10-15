"""Command line interface for survey2report."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from survey2report import __version__
from survey2report.charts import MAX_CHARTS
from survey2report.pipeline import DatasetOutput, discover_csvs, process_dataset

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_BAD_INPUT = 2
PREVIEW_FINDINGS = 3


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ``survey2report`` command.

    Returns:
        The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="survey2report",
        description="Turn a folder of messy survey CSVs into PowerPoint reports.",
        epilog=(
            "Each dataset produces output/<name>/report.pptx plus cleaned data, "
            "logs and charts."
        ),
    )
    parser.add_argument(
        "-i", "--input", type=Path, required=True, help="folder containing survey CSV files"
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("output"), help="folder for the reports"
    )
    parser.add_argument(
        "-c",
        "--max-charts",
        type=int,
        default=MAX_CHARTS,
        help=f"charts per dataset (default {MAX_CHARTS}, keeps the deck at 3-5 charts)",
    )
    parser.add_argument("--version", action="version", version=f"survey2report {__version__}")
    return parser


def use_utf8_console() -> None:
    """Let stdout and stderr print non-ASCII text on legacy Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def _describe(output: DatasetOutput) -> list[str]:
    """Format the progress lines for one processed dataset."""
    lines = [
        f"  {output.source.name}: {output.rows} rows, {len(output.charts)} charts "
        f"-> {output.directory}"
    ]
    lines += [f"      {finding}" for finding in output.findings[:PREVIEW_FINDINGS]]
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line interface.

    Args:
        argv: Argument list to parse. Defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code: 0 on success, 1 if a dataset failed, 2 for bad input.
    """
    use_utf8_console()
    args = build_parser().parse_args(argv)

    if not args.input.is_dir():
        print(f"error: input folder not found: {args.input}", file=sys.stderr)
        return EXIT_BAD_INPUT
    files = discover_csvs(args.input)
    if not files:
        print(f"error: no CSV files found in {args.input}", file=sys.stderr)
        return EXIT_BAD_INPUT

    print(f"survey2report {__version__}: {len(files)} dataset(s) -> {args.output}")
    failures = 0
    for path in files:
        try:
            output = process_dataset(path, args.output, max_charts=args.max_charts)
        except (OSError, ValueError, KeyError) as error:
            failures += 1
            print(f"  FAILED {path.name}: {error}", file=sys.stderr)
            continue
        for line in _describe(output):
            print(line)

    print(f"done: {len(files) - failures}/{len(files)} report(s) written to {args.output}")
    return EXIT_FAILED if failures else EXIT_OK
