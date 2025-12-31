"""Match code/content against malicious signatures."""

import json
import re
from pathlib import Path
from re import Pattern

from chromeguard import data_path


class Signature:
    """Regex-based signature."""

    def __init__(self, name: str, pattern: str, severity: str) -> None:
        self.name = name
        self.pattern = pattern
        self.severity = severity
        self.regex: Pattern[str] = re.compile(pattern, re.IGNORECASE | re.MULTILINE)

    def match(self, content: str) -> bool:
        """Return True if pattern matches content."""
        return bool(self.regex.search(content))


class SignatureMatcher:
    """Load and evaluate signatures from JSON."""

    def __init__(self) -> None:
        sig_path = Path(data_path()) / "signatures.json"
        with sig_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        self.signatures: list[Signature] = [
            Signature(item["name"], item["pattern"], item.get("severity", "medium"))
            for item in raw.get("signatures", [])
        ]

    def scan_blob(self, content: str) -> list[dict[str, str]]:
        """Return list of matched signatures."""
        findings: list[dict[str, str]] = []
        for sig in self.signatures:
            if sig.match(content):
                findings.append({"name": sig.name, "severity": sig.severity})
        return findings


