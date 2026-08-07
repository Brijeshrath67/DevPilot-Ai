"""Security helpers: secret validation and safe path handling."""

import re
from pathlib import Path

from app.core.config import settings


def is_secret_value(value: str) -> bool:
    """Heuristic check for obvious secret material (tokens, keys, JWTs)."""
    if not value:
        return False
    patterns = [
        re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.\=\+]{24,}"),
        re.compile(r"(eyJ[a-zA-Z0-9_\-]+\.){2}[a-zA-Z0-9_\-]+"),  # JWT
        re.compile(r"(sk|pk|AKIA)[a-zA-Z0-9_\-]{16,}"),
    ]
    return any(pattern.search(value) for pattern in patterns)


def resolve_within_root(path: str | Path, root: str | Path) -> Path:
    """Resolve *path* and ensure it stays inside *root* (blocks path traversal)."""
    root_resolved = Path(root).resolve()
    candidate = (root_resolved / path).resolve()
    if not str(candidate).startswith(str(root_resolved)):
        raise ValueError(f"Path escapes configured data root: {path}")
    return candidate


def get_jwt_secret() -> str:
    return settings.jwt_secret_key
