import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path


class BaseAgent(ABC):
    """Abstract contract for all specialized agents."""

    @abstractmethod
    def handle(self, payload: dict) -> dict:
        raise NotImplementedError

    @staticmethod
    def resolve_scope_files(root_path: str, scope: str) -> list[str] | None:
        """Return relative paths of files changed since HEAD for the ``changes`` scope.

        Returns ``None`` (scan everything) when scope is not ``changes`` or the
        repository is not a git checkout.
        """
        if scope != "changes":
            return None
        root = Path(root_path)
        if not root.exists() or not (root / ".git").exists():
            return None
        try:
            git = shutil.which("git")
            if git is None:
                return None
            result = subprocess.run(  # noqa: S603
                [git, "-C", str(root), "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            if result.returncode != 0:
                return None
            return [line for line in result.stdout.splitlines() if line.strip()]
        except Exception:  # non-git or broken checkout falls back to full scan
            return None
