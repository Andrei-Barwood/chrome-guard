"""Lightweight behavior monitor (stub for Playwright-driven analysis)."""

import asyncio
from dataclasses import dataclass

SCRAPING_HINTS = ["chatgpt", "conversation", "deepseek", "prompt"]
SUSPICIOUS_FREQ_THRESHOLD = 60  # seconds


@dataclass
class NetworkEvent:
    """Network event captured from browser context."""

    url: str
    method: str
    status: int
    timestamp: float


@dataclass
class BehaviorFinding:
    """Finding from behavior analysis."""

    message: str
    severity: str


class BehaviorMonitor:
    """Monitor network and DOM activity via Playwright (simplified)."""

    def __init__(self, request_limit: int = 100) -> None:
        self.request_limit = request_limit

    async def analyze_requests(self, events: list[NetworkEvent]) -> list[BehaviorFinding]:
        """Inspect network events for suspicious domains and frequency."""
        findings: list[BehaviorFinding] = []
        if not events:
            return findings

        events_sorted = sorted(events, key=lambda e: e.timestamp)
        for event in events_sorted:
            if "chat" in event.url and "ai" in event.url:
                findings.append(
                    BehaviorFinding(f"Possible AI chat exfiltration to {event.url}", "high")
                )

        # frequency check
        for idx in range(1, len(events_sorted)):
            delta = events_sorted[idx].timestamp - events_sorted[idx - 1].timestamp
            if delta < SUSPICIOUS_FREQ_THRESHOLD:
                findings.append(BehaviorFinding("High frequency network calls", "medium"))
                break

        return findings

    async def analyze_dom(self, scripts: list[str]) -> list[BehaviorFinding]:
        """Inspect collected scripts for scraping hints."""
        findings: list[BehaviorFinding] = []
        content = "\n".join(scripts).lower()
        if any(hint in content for hint in SCRAPING_HINTS):
            findings.append(BehaviorFinding("DOM scraping patterns detected", "high"))
        if "localstorage" in content:
            findings.append(BehaviorFinding("LocalStorage access detected", "medium"))
        if "eval(" in content or "Function(" in content:
            findings.append(BehaviorFinding("Dynamic code execution detected", "medium"))
        return findings

    async def run(self) -> None:
        """Placeholder for future Playwright session execution."""
        await asyncio.sleep(0)  # no-op to keep interface async-friendly


