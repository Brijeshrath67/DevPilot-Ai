import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import httpx
from fastapi import UploadFile

DATA_ROOT = Path(__file__).resolve().parents[2] / "data" / "repositories"
DATA_ROOT.mkdir(parents=True, exist_ok=True)

class RepositoryStorageService:
    def __init__(self) -> None:
        self.data_root = DATA_ROOT

    def _extract_zip(self, zip_path: Path, destination: Path) -> Path:
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(destination)
        entries = [child for child in destination.iterdir() if child.is_dir()]
        # GitHub archives wrap files in a single "owner-repo-branch/" directory.
        # Use it only when there is exactly one top-level directory so arbitrary
        # user zips are rooted at the extraction destination instead.
        if len(entries) == 1:
            return entries[0]
        return destination

    def _download_github_archive(self, url: str, target_path: Path) -> Path:
        owner_repo_branch = self._parse_github_url(url)
        if not owner_repo_branch:
            raise ValueError("Unsupported GitHub URL format")

        owner, repo, branch = owner_repo_branch
        archive_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        with httpx.stream("GET", archive_url, timeout=60.0) as response:
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                for chunk in response.iter_bytes():
                    tmp_file.write(chunk)
                tmp_path = Path(tmp_file.name)

        extracted_path = self._extract_zip(tmp_path, target_path)
        tmp_path.unlink(missing_ok=True)
        return extracted_path

    def _parse_github_url(self, url: str) -> Optional[tuple[str, str, str]]:
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
