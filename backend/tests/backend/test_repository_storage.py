"""Unit tests for repository storage and file-content reading."""

import zipfile
from pathlib import Path

import pytest
from app.services.repository_storage_service import DATA_ROOT, RepositoryStorageService


@pytest.fixture()
def storage() -> RepositoryStorageService:
    return RepositoryStorageService()


def test_data_root_resolves_under_settings_data_root():
    # DATA_ROOT must live under the configured DATA_ROOT (hermetic storage).
    configured = Path(DATA_ROOT)
    assert configured.name == "repositories"
    assert configured.is_dir()


def test_read_repository_file_returns_content(storage, tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "app.py").write_text("def main():\n    pass\n", encoding="utf-8")

    content = storage.read_repository_file(root, "app.py")
    assert "def main()" in content


def test_read_repository_file_missing(storage, tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        storage.read_repository_file(tmp_path, "nope.py")


def test_read_repository_file_rejects_path_traversal(storage, tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    with pytest.raises(ValueError):
        storage.read_repository_file(root, "../../etc/passwd")


def test_read_repository_file_rejects_binary(storage, tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "image.bin").write_bytes(b"\x00\x01\x02binary")
    with pytest.raises(ValueError):
        storage.read_repository_file(root, "image.bin")


def test_resolve_repository_root_uses_recorded_path(storage, tmp_path: Path):
    recorded = tmp_path / "recorded"
    recorded.mkdir()
    assert storage.resolve_repository_root(999, str(recorded)) == recorded.resolve()


def test_resolve_repository_root_falls_back_when_stale(storage, tmp_path: Path):
    repo_id = 990001
    repo_dir = storage.data_root / str(repo_id)
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "main.py").write_text("print(1)\n", encoding="utf-8")

    resolved = storage.resolve_repository_root(repo_id, "/does/not/exist")
    assert resolved == repo_dir.resolve()
    assert storage.read_repository_file(resolved, "main.py") == "print(1)\n"
    (repo_dir / "main.py").unlink()
    repo_dir.rmdir()


def test_resolve_repository_root_missing_repo_raises(storage):
    with pytest.raises(ValueError):
        storage.resolve_repository_root(999999, None)


def test_extract_zip_unwraps_single_wrapper_dir(storage, tmp_path: Path):
    archive_path = tmp_path / "wrapped.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("owner-repo-main/README.md", "# wrapped\n")
        archive.writestr("owner-repo-main/src/app.py", "print(1)\n")

    extracted = storage._extract_zip(archive_path, tmp_path / "dest")
    assert extracted.name == "owner-repo-main"
    assert (extracted / "README.md").is_file()


def test_extract_zip_keeps_root_when_top_level_files_exist(storage, tmp_path: Path):
    archive_path = tmp_path / "mixed.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("README.md", "# mixed\n")
        archive.writestr("src/app.py", "print(1)\n")

    extracted = storage._extract_zip(archive_path, tmp_path / "dest")
    assert extracted == tmp_path / "dest"
    assert (extracted / "src/app.py").is_file()
    assert (extracted / "README.md").is_file()


def test_read_ipynb_content(storage, tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    nb_json = '{"cells": [{"cell_type": "code", "source": ["print(1)\\n"]}], "nbformat": 4}'
    (root / "analysis.ipynb").write_text(nb_json, encoding="utf-8")

    assert '"nbformat"' in storage.read_repository_file(root, "analysis.ipynb")
