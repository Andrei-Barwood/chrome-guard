"""Brave extension extractor."""

import os
from pathlib import Path


def default_profile_path() -> Path:
    """Return default Brave extensions directory."""
    env = os.environ.get("CHROMEGUARD_BRAVE_PROFILE")
    if env:
        return Path(env).expanduser()
    if os.name == "nt":
        return (
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "BraveSoftware/Brave-Browser/User Data/Default/Extensions"
        )
    return Path.home() / ".config/BraveSoftware/Brave-Browser/Default/Extensions"


def list_extensions(profile_path: Path | None = None) -> list[Path]:
    """List extension directories."""
    base = profile_path or default_profile_path()
    if not base.exists():
        return []
    return [p for p in base.iterdir() if p.is_dir()]


