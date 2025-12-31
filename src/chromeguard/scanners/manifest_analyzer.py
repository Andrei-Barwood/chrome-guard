"""Analyze Chrome/Edge extension manifests for risky patterns."""

import json
from pathlib import Path
from typing import Any, cast

import yaml

from chromeguard import data_path


class ManifestFinding:
    """Structured finding for manifest analysis."""

    def __init__(self, message: str, severity: str) -> None:
        self.message = message
        self.severity = severity

    def to_dict(self) -> dict[str, str]:
        """Return dict representation."""
        return {"message": self.message, "severity": self.severity}


class ManifestAnalyzer:
    """Scanner that applies static rules to manifest.json."""

    def __init__(self) -> None:
        dangerous_path = Path(data_path()) / "dangerous_permissions.yaml"
        with dangerous_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        self.high_risk: list[str] = data.get("high_risk", [])

    def load_manifest(self, manifest_path: str) -> dict[str, Any]:
        """Load manifest JSON from disk."""
        with Path(manifest_path).open("r", encoding="utf-8") as handle:
            return cast(dict[str, Any], json.load(handle))

    def analyze(self, manifest: dict[str, Any]) -> tuple[int, list[ManifestFinding]]:
        """Return (score, findings). Higher score == more risk."""
        findings: list[ManifestFinding] = []
        risk_score = 0

        permissions = manifest.get("permissions", []) or []
        if "<all_urls>" in permissions:
            findings.append(ManifestFinding('Permission "<all_urls>" detected', "high"))
            risk_score += 25

        risky = [perm for perm in permissions if perm in self.high_risk]
        if risky:
            findings.append(
                ManifestFinding(
                    f"High-risk permissions present: {', '.join(sorted(set(risky)))}", "high"
                )
            )
            risk_score += 20

        externally = manifest.get("externally_connectable", {})
        if isinstance(externally, dict):
            matches = externally.get("matches", [])
            if any(match == "*" or match.startswith("*://*") for match in matches):
                findings.append(ManifestFinding("externally_connectable allows wildcards", "high"))
                risk_score += 15

        csp = manifest.get("content_security_policy", "")
        if not csp:
            findings.append(ManifestFinding("Missing content_security_policy", "medium"))
            risk_score += 10
        elif "unsafe-eval" in csp or "unsafe-inline" in csp:
            findings.append(ManifestFinding("Weak CSP contains unsafe-eval/inline", "medium"))
            risk_score += 10

        wer = manifest.get("web_accessible_resources", [])
        if wer:
            findings.append(ManifestFinding("Web accessible resources declared", "info"))
            risk_score += 5
            if any(
                "*" in resource.get("resources", [])
                for resource in wer
                if isinstance(resource, dict)
            ):
                findings.append(
                    ManifestFinding("web_accessible_resources exposes wildcard", "high")
                )
                risk_score += 15

        background = manifest.get("background", {})
        if isinstance(background, dict):
            if background.get("persistent") is True:
                findings.append(ManifestFinding("Persistent background page enabled", "medium"))
                risk_score += 5

        risk_score = min(risk_score, 100)
        return risk_score, findings


