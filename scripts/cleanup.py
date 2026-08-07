#!/usr/bin/env python3
"""Remove local runtime data: the SQLite database and uploaded file stores.

Run standalone (no server required):

    python scripts/cleanup.py

WARNING: deletes ALL ingested repositories and analysis data in the local
development database. It never touches source code outside the app's own
data directories.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"

TARGETS = [
    BACKEND / "devpilot.db",
    BACKEND / "data",
]


def main() -> None:
    removed = []
    for target in TARGETS:
        if target.is_dir():
            shutil.rmtree(target)
            removed.append(target)
        elif target.is_file():
            target.unlink()
            removed.append(target)
    if removed:
        print("Removed:")
        for path in removed:
            print(f"  - {path}")
    else:
        print("Nothing to clean; database and data directories already absent.")
    print("Run `python scripts/seed.py` to rebuild the demo dataset.")


if __name__ == "__main__":
    main()
