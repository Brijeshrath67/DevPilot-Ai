import re
import shutil
import tempfile
import zipfile
from pathlib import Path

import httpx
from fastapi import UploadFile

from app.core.config import settings

# Resolve the repository storage root from settings so tests can point it at a
# temp directory (hermetic) instead of clobbering real data. Falls back to the
# historical location next to the backend package when DATA_ROOT is relative.
_repositories_root = Path(settings.data_root).expanduser()
if not _repositories_root.is_absolute():
    _repositories_root = Path(__file__).resolve().parents[2] / _repositories_root
DATA_ROOT = _repositories_root / "repositories"
DATA_ROOT.mkdir(parents=True, exist_ok=True)


class RepositoryStorageService:
    def __init__(self) -> None:
        self.data_root = DATA_ROOT

    def resolve_repository_root(self, repository_id: int, root_path: str | None) -> Path:
        """Return a usable filesystem root for a repository's files.

        Prefers the ``root_path`` recorded for the repository, but falls back to
        the canonical storage directory when that path is stale or missing (e.g.
        the repo was re-uploaded after the DB record was written).
        """
        if root_path and Path(root_path).is_dir():
            return Path(root_path).resolve()
        storage_dir = self.data_root / str(repository_id)
        if not storage_dir.is_dir():
            raise ValueError("Repository files not available on disk")
        subdirs = [child for child in storage_dir.iterdir() if child.is_dir()]
        return subdirs[0].resolve() if len(subdirs) == 1 else storage_dir.resolve()

    def _extract_zip(self, zip_path: Path, destination: Path) -> Path:
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(destination)
        children = [child for child in destination.iterdir()]
        # GitHub archives wrap files in a single "owner-repo-branch/" directory.
        # Only unwrap when the zip has exactly one top-level entry and it is a
        # directory; any zip with top-level files (e.g. a repo that mixes a
        # "src/" folder with a README) stays rooted at the extraction target.
        if len(children) == 1 and children[0].is_dir():
            return children[0]
        return destination

    def _download_github_archive(self, url: str, target_path: Path) -> Path:
        owner_repo_branch = self._parse_github_url(url)
        if not owner_repo_branch:
            raise ValueError("Unsupported GitHub URL format")

        owner, repo, branch = owner_repo_branch
        archive_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        with httpx.stream("GET", archive_url, timeout=60.0, follow_redirects=True) as response:
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                for chunk in response.iter_bytes():
                    tmp_file.write(chunk)
                tmp_path = Path(tmp_file.name)

        extracted_path = self._extract_zip(tmp_path, target_path)
        tmp_path.unlink(missing_ok=True)
        return extracted_path

    def _parse_github_url(self, url: str) -> tuple[str, str, str] | None:
        pattern = r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)(?:/tree/(?P<branch>[^/]+))?"
        match = re.search(pattern, url)
        if not match:
            return None
        owner = match.group("owner")
        repo = match.group("repo").removesuffix(".git")
        branch = match.group("branch") or "main"
        return owner, repo, branch

    def store_github_repository(self, url: str, repository_id: int) -> Path:
        target_dir = self.data_root / str(repository_id)
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        extracted = self._download_github_archive(url, target_dir)
        return extracted

    def store_archive(self, archive_file: UploadFile, repository_id: int) -> Path:
        target_dir = self.data_root / str(repository_id)
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        temp_zip = target_dir / "upload.zip"
        with temp_zip.open("wb") as out_file:
            out_file.write(archive_file.file.read())

        extracted = self._extract_zip(temp_zip, target_dir)
        temp_zip.unlink(missing_ok=True)
        return extracted

    def read_repository_file(self, root_path: str, relative_path: str) -> str:
        """Return the UTF-8 text content of a repository file by its relative path.

        Resolves the requested path inside ``root_path`` and rejects any path
        that escapes the repository root (path traversal guard).
        """
        root = Path(root_path).resolve()
        target = (root / relative_path).resolve()
        if root != target and root not in target.parents:
            raise ValueError("File path escapes the repository root")

        if not target.is_file():
            raise FileNotFoundError(relative_path)

        raw = target.read_bytes()
        if b"\x00" in raw[:8192]:
            raise ValueError("Binary files are not supported")
        return raw.decode("utf-8", errors="replace")
