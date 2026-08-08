"""Code-quality scanner: flags real maintainability signals in source files.

Complementary to :class:`SecuritySkill`. Produces MINOR/MEDIUM findings for
common maintainability smells that the security scanner intentionally ignores,
so the code review reflects the repository's actual code.
"""

import json
import re
from pathlib import Path
from typing import Any

SOURCE_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".java",
    ".go",
    ".php",
    ".rb",
    ".cs",
    ".kt",
    ".swift",
    ".sh",
    ".bash",
    ".sql",
    ".ipynb",
}

IGNORED_DIRS = {"venv", ".venv", "node_modules", ".git", "__pycache__", "dist", "build"}

_TODO_PATTERN = re.compile(r"#\s*(TODO|FIXME|HACK|XXX)[\s:]")
_BARE_EXCEPT_PATTERN = re.compile(r"^\s*except\s*:")
_DEBUG_PRINT_PATTERN = re.compile(r"^\s*print\s*\(")
_MAX_LINE_LENGTH = 120


def _read_lines(path: Path) -> list[str]:
    if path.suffix == ".ipynb":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cells = data.get("cells", []) if isinstance(data, dict) else []
            text = ""
            for cell in cells:
                source = cell.get("source", []) if isinstance(cell, dict) else []
                if isinstance(source, list):
                    text += "".join(source)
                elif isinstance(source, str):
                    text += source
            return text.splitlines()
        except Exception:  # malformed notebooks are skipped
            return []
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:  # unreadable files are skipped
        return []


class QualitySkill:
    def scan_repository(
        self, repository_path: str, files: list[str] | None = None, root: Path | None = None
    ) -> list[dict[str, Any]]:
        findings = []
        repo_root = root or Path(repository_path)
        if not repo_root.exists() or not repo_root.is_dir():
            return findings

        if files:
            targets = []
            for f in files:
                candidate = (repo_root / f).resolve()
                if candidate.is_relative_to(repo_root) and candidate.is_file():
                    targets.append(candidate)
        else:
            targets = [
                path
                for path in repo_root.rglob("*")
                if path.is_file()
                and path.suffix in SOURCE_EXTENSIONS
                and not any(part in path.parts for part in IGNORED_DIRS)
            ]

        for path in targets:
            lines = _read_lines(path)
            rel_path = str(path.relative_to(repo_root)).replace("\\", "/")
            for line_num, line in enumerate(lines, start=1):
                stripped = line.strip()
                if _TODO_PATTERN.search(line):
                    findings.append(
                        self._finding(
                            rel_path,
                            line_num,
                            "MINOR",
                            "Outstanding TODO/FIXME",
                            f"Leftover marker: `{stripped[:60]}`",
                            "Resolve or track the TODO/FIXME; leaving markers in the codebase hides real work.",
                        )
                    )
                if _BARE_EXCEPT_PATTERN.match(line):
                    findings.append(
                        self._finding(
                            rel_path,
                            line_num,
                            "MEDIUM",
                            "Bare except clause",
                            "A bare `except:` swallows every error, masking unexpected failures.",
                            "Catch specific exception types instead of a bare except.",
                        )
                    )
                if _DEBUG_PRINT_PATTERN.match(stripped) and not self._is_test_file(rel_path):
                    findings.append(
                        self._finding(
                            rel_path,
                            line_num,
                            "MINOR",
                            "Debug print() left in code",
                            f"`{stripped[:60]}` looks like leftover debug output.",
                            "Replace with structured logging or remove before shipping.",
                        )
                    )
                if len(line) > _MAX_LINE_LENGTH:
                    findings.append(
                        self._finding(
                            rel_path,
                            line_num,
                            "MINOR",
                            "Line exceeds 120 characters",
                            f"Line is {len(line)} characters long; long lines hurt readability.",
                            "Break the line into smaller, readable chunks.",
                        )
                    )
        return findings

    @staticmethod
    def _finding(
        file: str,
        line: int,
        severity: str,
        vulnerability: str,
        description: str,
        recommendation: str,
    ) -> dict:
        return {
            "file": file,
            "line": line,
            "severity": severity,
            "vulnerability": vulnerability,
            "description": description,
            "recommendation": recommendation,
        }

    @staticmethod
    def _is_test_file(rel_path: str) -> bool:
        parts = rel_path.replace("\\", "/").split("/")
        return any("test" in part.lower() for part in parts)
