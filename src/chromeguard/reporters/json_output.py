"""JSON report generation."""

import json
from pathlib import Path
from typing import Any


def write_json(report: list[dict[str, Any]], path: str) -> None:
    """Write report to JSON file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)


