from pathlib import Path

from chromeguard.scanners.manifest_analyzer import ManifestAnalyzer


def test_malicious_manifest_scores_high() -> None:
    analyzer = ManifestAnalyzer()
    manifest = analyzer.load_manifest(
        str(Path(__file__).parent / "fixtures" / "malicious_manifest.json")
    )
    score, findings = analyzer.analyze(manifest)
    assert score >= 25
    assert any("High-risk permissions" in f.message for f in findings)


def test_safe_manifest_scores_low() -> None:
    analyzer = ManifestAnalyzer()
    manifest = analyzer.load_manifest(
        str(Path(__file__).parent / "fixtures" / "safe_manifest.json")
    )
    score, _ = analyzer.analyze(manifest)
    assert score <= 20

