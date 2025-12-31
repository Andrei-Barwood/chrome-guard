"""CSV report generation."""

import csv
from pathlib import Path
from typing import Any


def write_csv(report: list[dict[str, Any]], path: str) -> None:
    """Write report to CSV file."""
    if not report:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    headers = sorted(report[0].keys())
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(report)


