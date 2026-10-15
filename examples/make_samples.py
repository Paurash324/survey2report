"""Regenerate the messy sample survey CSVs in ``examples/``.

The samples are committed to the repository, so this script only needs to be
run when the fixtures themselves should change.

Usage:
    python examples/make_samples.py
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

from messy_builders import SEED, customers, employees, events, health, pricing

HERE = Path(__file__).parent

DATASETS = {
    "employee_engagement_2024.csv": employees,
    "customer_satisfaction_q1.csv": customers,
    "event_feedback.csv": events,
    "product_pricing_survey.csv": pricing,
    "public_health_checkup.csv": health,
}


def write_csv(name: str, header: list[str], rows: list[list[str]], bom: bool = False) -> None:
    """Write one sample CSV next to this script."""
    with (HERE / name).open("w", newline="", encoding="utf-8-sig" if bom else "utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    print(f"wrote {name} ({len(rows)} data rows)")


def main() -> None:
    """Write every sample CSV into the examples directory."""
    for name, builder in DATASETS.items():
        rng = random.Random(f"{SEED}-{name}")
        header, rows = builder(rng)
        write_csv(name, header, rows, bom=name == "event_feedback.csv")


if __name__ == "__main__":
    main()
