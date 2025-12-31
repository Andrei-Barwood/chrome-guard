"""ChromeGuard CLI entrypoint."""

import asyncio
import json
from pathlib import Path
from typing import Any, cast

import typer
from rich.progress import Progress

from chromeguard import data_path
from chromeguard.extractors import brave, chrome, edge
from chromeguard.reporters import csv_export, json_output, terminal_ui
from chromeguard.scanners.behavior_monitor import BehaviorMonitor, NetworkEvent
from chromeguard.scanners.manifest_analyzer import ManifestAnalyzer
from chromeguard.scanners.signature_matcher import SignatureMatcher
from chromeguard.utils import logger

app = typer.Typer(help="Audit Chrome/Edge extensions for malicious patterns.")
BROWSER_BUILTINS = {
    # Chrome built-in extensions (commonly missing manifest at root; live under version dirs)
    "ghbmnnjooekpmoecnnnilnnbdlolhkhi",  # Chrome Web Store
    "nmmhkkegccagdldgiimedpiccmgmieda",  # Docs Offline / similar
}


def _load_whitelist() -> list[str]:
    path = Path(data_path()) / "whitelist.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    allowed = data.get("allowed", [])
    return cast(list[str], allowed)


def _save_whitelist(ext_ids: list[str]) -> None:
    path = Path(data_path()) / "whitelist.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump({"allowed": sorted(set(ext_ids))}, handle, indent=2)


def _choose_extractor(browser: str):
    browser_lower = browser.lower()
    if browser_lower == "chrome":
        return chrome
    if browser_lower == "edge":
        return edge
    if browser_lower == "brave":
        return brave
    raise typer.BadParameter("Browser must be chrome, edge, or brave.")


def _collect_js_files(extension_dir: Path) -> list[Path]:
    return [p for p in extension_dir.rglob("*.js") if p.is_file()]


def _find_manifest_path(extension_dir: Path) -> Path | None:
    """Return manifest.json path either at root or inside versioned subdir."""
    root_manifest = extension_dir / "manifest.json"
    if root_manifest.exists():
        return root_manifest
    # Look for versioned subdirectories and pick highest (sorted)
    candidates = [p for p in extension_dir.iterdir() if p.is_dir()]
    versioned = sorted(candidates, key=lambda p: p.name, reverse=True)
    for candidate in versioned:
        mpath = candidate / "manifest.json"
        if mpath.exists():
            return mpath
    return None


def _risk_label(score: int) -> str:
    if score >= 70:
        return "Remove immediately"
    if score >= 40:
        return "Review manually"
    return "Safe"


def _scan_extension(
    extension_dir: Path, manifest_analyzer: ManifestAnalyzer, matcher: SignatureMatcher
) -> dict[str, Any]:
    manifest_path = _find_manifest_path(extension_dir)
    if not manifest_path:
        return {
            "extension": extension_dir.name,
            "score": 0,
            "recommendation": "Review manually",
            "findings": ["manifest.json missing"],
        }

    manifest = manifest_analyzer.load_manifest(str(manifest_path))
    score, manifest_findings = manifest_analyzer.analyze(manifest)

    js_files = _collect_js_files(extension_dir)
    sig_findings: list[dict[str, str]] = []
    for js_file in js_files:
        content = js_file.read_text(encoding="utf-8", errors="ignore")
        sig_findings.extend(matcher.scan_blob(content))

    combined_findings: list[str] = [f"{f.severity}: {f.message}" for f in manifest_findings]
    combined_findings.extend([f"{f['severity']}: {f['name']}" for f in sig_findings])

    total_score = min(score + len(sig_findings) * 5, 100)

    return {
        "extension": manifest.get("name", extension_dir.name),
        "id": extension_dir.name,
        "score": total_score,
        "recommendation": _risk_label(total_score),
        "findings": combined_findings,
    }


@app.callback()
def main(debug: bool = typer.Option(False, "--debug", help="Enable debug logging")) -> None:
    """Configure logging."""
    logger.configure_logging(debug)


@app.command()
def scan(
    browser: str = typer.Option("chrome", "--browser", "-b", help="chrome|edge|brave"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output JSON file"),
    csv: str | None = typer.Option(None, "--csv", help="Optional CSV export path"),
    extensions_path: str | None = typer.Option(
        None, "--extensions-path", help="Override extension directory"
    ),
) -> None:
    """Scan installed extensions for risky patterns."""
    extractor = _choose_extractor(browser)
    base_path = Path(extensions_path) if extensions_path else extractor.default_profile_path()
    ext_dirs = extractor.list_extensions(base_path)

    manifest_analyzer = ManifestAnalyzer()
    matcher = SignatureMatcher()
    whitelist = set(_load_whitelist()) | BROWSER_BUILTINS

    report: list[dict[str, Any]] = []
    with Progress() as progress:
        task = progress.add_task("Scanning extensions", total=len(ext_dirs))
        for ext_dir in ext_dirs:
            if ext_dir.name in whitelist:
                progress.advance(task)
                continue
            result = _scan_extension(ext_dir, manifest_analyzer, matcher)
            report.append(result)
            progress.advance(task)

    if output:
        json_output.write_json(report, output)
    if csv:
        csv_export.write_csv(report, csv)

    terminal_ui.print_report(report)


@app.command()
def check(extension_id: str, browser: str = typer.Option("chrome", "--browser", "-b")) -> None:
    """Check a single extension id."""
    extractor = _choose_extractor(browser)
    base_path = extractor.default_profile_path()
    target = base_path / extension_id
    if not target.exists():
        typer.echo(f"Extension {extension_id} not found at {target}")
        raise typer.Exit(code=1)

    manifest_analyzer = ManifestAnalyzer()
    matcher = SignatureMatcher()
    result = _scan_extension(target, manifest_analyzer, matcher)
    terminal_ui.print_report([result])


@app.command()
def whitelist(
    action: str = typer.Argument(..., help="add|list"),
    extension_id: str | None = typer.Argument(None, help="Extension id to add"),
) -> None:
    """Manage whitelist."""
    items = _load_whitelist()
    if action == "list":
        typer.echo("\n".join(items) if items else "Whitelist empty")
        return
    if action == "add":
        if not extension_id:
            raise typer.BadParameter("Extension id required for add")
        items.append(extension_id)
        _save_whitelist(items)
        typer.echo(f"Added {extension_id} to whitelist")
        return
    raise typer.BadParameter("Action must be add or list")


@app.command()
def update() -> None:
    """Refresh threat database (local placeholder)."""
    data_dir = Path(data_path())
    signatures = data_dir / "signatures.json"
    typer.echo(f"Update signatures by editing {signatures} or running scripts/update_signatures.py")


@app.command()
def watch(
    browser: str = typer.Option("chrome", "--browser", "-b"),
    interval: int = typer.Option(60, "--interval", "-i", help="Polling interval seconds"),
    iterations: int = typer.Option(1, "--iterations", help="How many loops to run"),
) -> None:
    """Monitor behavior in a loop (placeholder without Playwright launch)."""
    extractor = _choose_extractor(browser)
    base_path = extractor.default_profile_path()
    monitor = BehaviorMonitor()
    manifest_analyzer = ManifestAnalyzer()
    matcher = SignatureMatcher()
    loop = asyncio.get_event_loop()

    for _ in range(iterations):
        ext_dirs = extractor.list_extensions(base_path)
        report: list[dict[str, Any]] = []
        for ext_dir in ext_dirs:
            result = _scan_extension(ext_dir, manifest_analyzer, matcher)
            # simulate behavior analysis with empty events/scripts
            behavior_findings = loop.run_until_complete(
                monitor.analyze_requests(
                    [
                        NetworkEvent(
                            url="https://example.com/chat",
                            method="GET",
                            status=200,
                            timestamp=0.0,
                        )
                    ]
                )
            )
            result["findings"].extend([f"{f.severity}: {f.message}" for f in behavior_findings])
            report.append(result)
        terminal_ui.print_report(report)
        if _ < iterations - 1:
            typer.echo(f"Sleeping {interval}s before next iteration...")
            loop.run_until_complete(asyncio.sleep(interval))


