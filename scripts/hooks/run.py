#!/usr/bin/env python3
"""Run a command inside a project subdirectory for pre-commit hooks.

Pre-commit does not change the working directory for ``language: system``
hooks across all versions, so these wrappers switch into the backend or
frontend directory before executing the real command.

Usage::

    python scripts/hooks/run.py <subdir> <command> [args...]
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("usage: python scripts/hooks/run.py <subdir> <command> [args...]")

    subdir = ROOT / sys.argv[1]
    if not subdir.is_dir():
        sys.exit(f"subdirectory does not exist: {subdir}")

    os.chdir(subdir)
    result = subprocess.run(sys.argv[2:], shell=os.name == "nt", check=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
