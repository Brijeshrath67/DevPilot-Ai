"""Tests for the Repository Analyzer agent."""

from pathlib import Path
from unittest.mock import MagicMock

from app.agents.repository_analyzer import RepositoryAnalyzerAgent
from app.services.database_service import DatabaseService
from app.services.parser_service import ParserService

PARSED = {
    "project_summary": "Rule-based project summary.",
    "architecture_summary": "Architecture summary.",
    "languages": ["Python"],
    "frameworks": ["FastAPI"],
    "dependencies": ["pydantic"],
}


def _repo(root_path: str | None = None) -> MagicMock:
    repo = MagicMock()
    repo.id = 1
    repo.name = "TestRepo"
    repo.root_path = root_path
    return repo


def _agent(llm=None, repo_root: str | None = None) -> tuple[RepositoryAnalyzerAgent, MagicMock]:
    parser = MagicMock(spec=ParserService)
    parser.analyze_repository.return_value = dict(PARSED)
    db = MagicMock(spec=DatabaseService)
    db.get_repository.return_value = _repo(root_path=repo_root)
    return RepositoryAnalyzerAgent(parser, db, llm=llm), db, parser


def test_missing_repository_id_returns_error():
    agent, _, _ = _agent()
    assert agent.handle({}) == {"error": "Missing repository_id"}


def test_repository_not_found_returns_error():
    agent, db, _ = _agent()
    db.get_repository.return_value = None
    assert agent.handle({"repository_id": "99"}) == {"error": "Repository not found"}


def test_analyzes_and_persists_summary(tmp_path: Path):
    agent, db, parser = _agent(repo_root=str(tmp_path))

    result = agent.handle({"repository_id": "1", "analysis_scope": "full"})

    parser.analyze_repository.assert_called_once_with("1", scope="full")
    assert result["summary"]["project_summary"] == PARSED["project_summary"]
    assert result["summary"]["languages"] == ["Python"]
    db.save_analysis_report.assert_called_once_with(1, "repository_analysis", PARSED)
    db.update_repository_summary.assert_called_once_with(1, PARSED["project_summary"], PARSED["architecture_summary"])


def test_skips_file_indexing_without_root_path():
    agent, db, _ = _agent(repo_root=None)

    agent.handle({"repository_id": "1"})

    db.save_repository_files.assert_not_called()


def test_indexes_files_and_skips_ignored_directories(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# readme\n", encoding="utf-8")
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "leak.js").write_text("var x = 1;\n", encoding="utf-8")

    agent, db, _ = _agent(repo_root=str(tmp_path))

    agent.handle({"repository_id": "1"})

    files = db.save_repository_files.call_args[0][1]
    by_path = {f["file_path"]: f for f in files}
    assert set(by_path) == {"src/app.py", "README.md"}
    assert by_path["src/app.py"]["language"] == "Python"
    assert by_path["src/app.py"]["file_type"] == "source"
    assert by_path["README.md"]["language"] == "Markdown"
    assert by_path["README.md"]["file_type"] == "file"
    assert by_path["src/app.py"]["checksum"]  # sha256 present


def test_uses_llm_when_real_key_present(tmp_path: Path):
    llm = MagicMock()
    llm.api_key = "real_key"
    llm.generate.return_value = "Groq-enhanced summary."
    agent, _, _ = _agent(llm=llm, repo_root=str(tmp_path))

    result = agent.handle({"repository_id": "1"})

    assert result["summary"]["project_summary"] == "Groq-enhanced summary."
    llm.generate.assert_called_once()
    assert llm.generate.call_args.kwargs == {"temperature": 0.2, "max_tokens": 160}


def test_skips_llm_for_mock_key(tmp_path: Path):
    llm = MagicMock()
    llm.api_key = "mock_key"
    agent, _, _ = _agent(llm=llm, repo_root=str(tmp_path))

    result = agent.handle({"repository_id": "1"})

    assert result["summary"]["project_summary"] == PARSED["project_summary"]
    llm.generate.assert_not_called()
