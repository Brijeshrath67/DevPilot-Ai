"""Tests for the Security Audit agent."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

from app.agents.security_agent import SecurityAgent
from app.services.database_service import DatabaseService


def _agent(root_path: str | None = None) -> tuple[SecurityAgent, MagicMock]:
    db = MagicMock(spec=DatabaseService)
    repo = MagicMock()
    repo.id = 1
    repo.root_path = root_path
    db.get_repository.return_value = repo
    return SecurityAgent(db), db


def test_no_repo_returns_clean_default():
    db = MagicMock(spec=DatabaseService)
    db.get_repository.return_value = None
    agent = SecurityAgent(db)

    result = agent.handle({"repository_id": "1"})

    assert result == {"security_score": 100.0, "issues": [], "recommendations": []}


def test_no_root_path_returns_clean_review():
    agent, _ = _agent(root_path=None)

    result = agent.handle({"repository_id": "1"})

    assert result["security_score"] == 100.0
    assert result["issues"] == []
    assert result["recommendations"] == []


def test_full_scan_returns_graded_issues_and_score(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        'api_key = "sk-super-secret-value-1234567890"\nresult = eval(user_input)\n',
        encoding="utf-8",
    )
    agent, _ = _agent(root_path=str(tmp_path))

    result = agent.handle({"repository_id": "1"})

    assert result["security_score"] == 65.0
    assert any(i["severity"] == "CRITICAL" for i in result["issues"])
    assert any(r.startswith("CRITICAL -") for r in result["recommendations"])


def test_high_findings_include_severity_prefix(tmp_path: Path):
    (tmp_path / "db.py").write_text(
        'cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")\n',
        encoding="utf-8",
    )
    agent, _ = _agent(root_path=str(tmp_path))

    result = agent.handle({"repository_id": "1"})

    assert any(r.startswith("HIGH -") for r in result["recommendations"])


def test_full_scan_returns_scan_metadata(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        'api_key = "sk-super-secret-value-1234567890"\nresult = eval(user_input)\n',
        encoding="utf-8",
    )
    agent, _ = _agent(root_path=str(tmp_path))

    result = agent.handle({"repository_id": "1"})

    assert result["files_scanned"] == 1
    assert result["patterns_checked"] > 5
    assert result["scan_time_ms"] >= 0


def test_file_scope_restricts_scan(tmp_path: Path):
    (tmp_path / "app.py").write_text('api_key = "sk-super-secret-value-1234567890"\n', encoding="utf-8")
    (tmp_path / "other.py").write_text('api_key = "sk-super-secret-value-0987654321"\n', encoding="utf-8")
    agent, _ = _agent(root_path=str(tmp_path))

    result = agent.handle({"repository_id": "1", "files": ["app.py"]})

    assert {i["file"] for i in result["issues"]} == {"app.py"}
    assert result["files_scanned"] == 1


def _git_repo(tmp_path: Path) -> Path:
    (tmp_path / "app.py").write_text('api_key = "sk-super-secret-value-1234567890"\n', encoding="utf-8")
    (tmp_path / "db.py").write_text("x = 1\n", encoding="utf-8")
    for command in [
        ["git", "init", "-q", "-b", "main"],
        ["git", "-C", ".", "config", "user.email", "test@example.com"],
        ["git", "-C", ".", "config", "user.name", "Test"],
        ["git", "-C", ".", "add", "."],
        ["git", "-C", ".", "commit", "-q", "-m", "initial"],
    ]:
        subprocess.run(command, cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def test_changes_scope_audits_only_modified_files(tmp_path: Path):
    repo_root = _git_repo(tmp_path)
    (repo_root / "app.py").write_text("password = 'hunter2secret'\nsubprocess.run(cmd, shell=True)\n", encoding="utf-8")
    agent, _ = _agent(root_path=str(repo_root))

    result = agent.handle({"repository_id": "1", "review_scope": "changes"})

    assert {i["file"] for i in result["issues"]} == {"app.py"}
    assert any(r.startswith("Audit scope: 1 file(s)") for r in result["recommendations"])


def test_changes_scope_falls_back_to_full_scan_without_git(tmp_path: Path):
    (tmp_path / "app.py").write_text('api_key = "sk-super-secret-value-1234567890"\n', encoding="utf-8")
    agent, _ = _agent(root_path=str(tmp_path))

    result = agent.handle({"repository_id": "1", "review_scope": "changes"})

    assert any(i["file"] == "app.py" for i in result["issues"])
    assert not any(r.startswith("Audit scope:") for r in result["recommendations"])
