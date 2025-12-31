"""ChromeGuard package."""

import os
from pathlib import Path

__all__ = ["data_path"]


def data_path() -> str:
    """Return path to data directory (env override for tests/custom)."""
    env_path = os.environ.get("CHROMEGUARD_DATA")
    if env_path:
        return str(Path(env_path).expanduser())
    return str(Path(__file__).resolve().parent.parent.parent / "data")

