"""Edge (Chromium) extension extractor."""

import os
from pathlib import Path


def default_profile_path() -> Path:
    """Return default Edge extensions directory."""
    env = os.environ.get("CHROMEGUARD_EDGE_PROFILE")
    if env:
        return Path(env).expanduser()
    if os.name == "nt":
        return (
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Microsoft/Edge/User Data/Default/Extensions"
        )
    return Path.home() / ".config/microsoft-edge/Default/Extensions"


def list_extensions(profile_path: Path | None = None) -> list[Path]:
    """List extension directories."""
    base = profile_path or default_profile_path()
    if not base.exists():
        return []
    return [p for p in base.iterdir() if p.is_dir()]


