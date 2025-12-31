"""Terminal UI helpers using Rich."""

from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


def print_report(report: list[dict[str, Any]]) -> None:
    """Print report in table format."""
    if not report:
        console.print("[green]No findings[/green]")
        return
    headers = sorted(report[0].keys())
    table = Table(title="ChromeGuard Report")
    for key in headers:
        table.add_column(key)
    for item in report:
        table.add_row(*(str(item.get(key, "")) for key in headers))
    console.print(table)


