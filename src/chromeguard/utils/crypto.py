"""Crypto helpers."""

from hashlib import sha256
from pathlib import Path


def sha256_file(path: str) -> str:
    """Compute SHA-256 hash for a file."""
    digest = sha256()
    file_path = Path(path)
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


