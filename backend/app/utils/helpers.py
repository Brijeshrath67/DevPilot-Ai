"""Shared backend utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from app.core.constants import IGNORED_DIRECTORIES


def sha256_checksum(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()


def is_ignored_path(path: Path) -> bool:
    """Return True when *path* sits inside a directory we never index or scan."""
    return any(part in path.parts for part in IGNORED_DIRECTORIES)


def safe_json_dumps(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, default=str)
