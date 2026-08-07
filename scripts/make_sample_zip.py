"""Build a ZIP archive of a repository directory.

Used by Playwright e2e tests and CI to produce the sample fixture archive.
This keeps archive generation deterministic across platforms.

Usage:
    python scripts/make_sample_zip.py <source_dir> <output_zip>
"""

import sys
import zipfile
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    source_dir = Path(sys.argv[1])
    output_zip = Path(sys.argv[2])

    if not source_dir.is_dir():
        print(f"Source directory does not exist: {source_dir}")
        return 1

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source_dir).as_posix())

    print(f"Created {output_zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
