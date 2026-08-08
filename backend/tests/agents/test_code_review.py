"""Tests for the Code Review agent."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

from app.agents.code_review import CodeReviewAgent
from app.services.database_service import DatabaseService


def _repo(root_path: str | None = None) -> MagicMock:
    repo = MagicMock()
    repo.id = 1
    repo.name = "ReviewRepo"
    repo.root_path = root_path
    return repo


def _agent(llm=None, repo_root: str | None = None) -> CodeReviewAgent:
    db = MagicMock(spec=DatabaseService)
    db.get_repository.return_value = _repo(root_path=repo_root)
    return CodeReviewAgent(db, llm=llm)


def _insecure_repo(tmp_path: Path) -> Path:
    (tmp_path / "app.py").write_text(
        'api_key = "sk-super-secret-value-1234567890"\nresult = eval(user_input)\n',
        encoding="utf-8",
    )
    (tmp_path / "db.py").write_text(
        'cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")\n',
        encoding="utf-8",
    )
    return tmp_path


def test_missing_repository_returns_error():
    db = MagicMock(spec=DatabaseService)
    db.get_repository.return_value = None
    agent = CodeReviewAgent(db, llm=None)
    assert agent.handle({"repository_id": "1"}) == {"error": "Repository not found"}


def test_no_root_path_produces_clean_review():
    agent = _agent(llm=None, repo_root=None)

    result = agent.handle({"repository_id": "1"})

    assert result["issues"] == []
    assert result["recommendations"] == []
    assert result["security_score"] == 100.0


def test_rule_based_review_grades_findings(tmp_path: Path):
    agent = _agent(llm=None, repo_root=str(_insecure_repo(tmp_path)))

    result = agent.handle({"repository_id": "1"})

    assert {i["severity"] for i in result["issues"]} == {"CRITICAL", "HIGH", "MEDIUM"}
    assert result["security_score"] == 50.0


def test_recommendations_cover_critical_and_high_only(tmp_path: Path):
    agent = _agent(llm=None, repo_root=str(_insecure_repo(tmp_path)))

    result = agent.handle({"repository_id": "1"})

    recs = result["recommendations"]
    assert any(r.startswith("CRITICAL -") for r in recs)
    assert any(r.startswith("HIGH -") for r in recs)
    assert not any(r.startswith("MEDIUM -") for r in recs)


def test_llm_review_appended_with_real_key(tmp_path: Path):
    llm = MagicMock()
    llm.api_key = "real_key"
    llm.provider = "huggingface"
    llm.generate.return_value = "Maintainability concern: split helpers."
    agent = _agent(llm=llm, repo_root=str(_insecure_repo(tmp_path)))

    result = agent.handle({"repository_id": "1"})

    assert any(r.startswith("LLM review (huggingface):") for r in result["recommendations"])
    llm.generate.assert_called_once()


def test_llm_review_includes_scope_and_target_files(tmp_path: Path):
    llm = MagicMock()
    llm.api_key = "real_key"
    llm.generate.return_value = "Review notes."
    agent = _agent(llm=llm, repo_root=str(_insecure_repo(tmp_path)))

    agent.handle(
        {
            "repository_id": "1",
            "review_scope": "critical",
            "files": ["src/app.py", "src/db.py"],
        }
    )

    prompt = llm.generate.call_args[0][0]
    assert "critical" in prompt
    assert "src/app.py, src/db.py" in prompt


def test_llm_failure_is_ignored(tmp_path: Path):
    llm = MagicMock()
    llm.api_key = "real_key"
    llm.generate.return_value = "LLM request failed (timeout). Falling back to local rules."
    agent = _agent(llm=llm, repo_root=str(_insecure_repo(tmp_path)))

    result = agent.handle({"repository_id": "1"})

    assert not any(r.startswith("LLM review") for r in result["recommendations"])


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


def test_changes_scope_reviews_only_modified_files(tmp_path: Path):
    repo_root = _git_repo(tmp_path)
    (repo_root / "app.py").write_text(
        "api_key = 'sk-super-secret-value-1234567890'\nprint('debug output')\nx = '12345678901234567890'\n",
        encoding="utf-8",
    )
    agent = _agent(llm=None, repo_root=str(repo_root))

    result = agent.handle({"repository_id": "1", "review_scope": "changes"})

    files = {i["file"] for i in result["issues"]}
    assert files == {"app.py"}
    assert any(r.startswith("Review scope: 1 file(s)") for r in result["recommendations"])


def test_changes_scope_falls_back_to_full_scan_without_git(tmp_path: Path):
    agent = _agent(llm=None, repo_root=str(_insecure_repo(tmp_path)))

    result = agent.handle({"repository_id": "1", "review_scope": "changes"})

    assert any(i["file"] == "app.py" for i in result["issues"])
    assert not any(r.startswith("Review scope:") for r in result["recommendations"])
