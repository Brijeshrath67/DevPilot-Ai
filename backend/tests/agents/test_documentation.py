"""Tests for the Documentation agent and its repo-grounded service."""

from unittest.mock import MagicMock

from app.agents.documentation import DocumentationAgent
from app.services.database_service import DatabaseService
from app.services.documentation_service import DocumentationService


def _repo(name: str = "Sample Repo", summary: str = "A sample repository for testing.") -> MagicMock:
    repo = MagicMock()
    repo.id = 1
    repo.name = name
    repo.summary = summary
    return repo


def _agent(llm=None, repo=None) -> tuple[DocumentationAgent, MagicMock]:
    db = MagicMock(spec=DatabaseService)
    db.get_repository.return_value = repo or _repo()
    return DocumentationAgent(DocumentationService(llm), db), db


def test_missing_repository_returns_error():
    db = MagicMock(spec=DatabaseService)
    db.get_repository.return_value = None
    agent = DocumentationAgent(DocumentationService(None), db)
    assert agent.handle({"repository_id": "1"}) == {"error": "Repository not found"}


def test_defaults_to_readme_with_repo_grounding():
    agent, _ = _agent(llm=None)
    result = agent.handle({"repository_id": "1"})
    doc = result["documents"][0]
    assert doc["type"] == "README"
    assert doc["title"] == "Sample Repo — README"
    assert "Sample Repo" in doc["content"]
    assert "A sample repository for testing." in doc["content"]


def test_generates_requested_doc_types():
    llm = MagicMock(spec=["generate"])
    llm.generate.return_value = "# LLM README"
    agent, _ = _agent(llm=llm)

    result = agent.handle({"repository_id": "1", "doc_types": ["readme", "changelog"]})

    assert {d["type"] for d in result["documents"]} == {"readme", "changelog"}
    assert result["documents"][0]["content"] == "# LLM README"


def test_passes_target_files_to_service():
    llm = MagicMock(spec=["generate"])
    llm.generate.return_value = "content"
    agent, _ = _agent(llm=llm)

    agent.handle({"repository_id": "1", "doc_types": ["api"], "target_files": ["src/main.py", "src/models.py"]})

    prompt = llm.generate.call_args[0][0]
    assert "src/main.py, src/models.py" in prompt


def test_falls_back_to_template_when_llm_fails():
    llm = MagicMock(spec=["generate"])
    llm.generate.return_value = "LLM request failed (boom). Falling back to local rules."
    agent, _ = _agent(llm=llm)

    result = agent.handle({"repository_id": "1", "doc_types": ["changelog"]})

    content = result["documents"][0]["content"]
    assert content.startswith("# Changelog")
    assert "Sample Repo" in content


def test_llm_prompt_is_repo_grounded_and_forbids_placeholders():
    llm = MagicMock(spec=["generate"])
    llm.generate.return_value = "content"
    agent, _ = _agent(llm=llm)

    agent.handle({"repository_id": "1", "doc_types": ["readme"]})

    prompt = llm.generate.call_args[0][0]
    assert "Sample Repo" in prompt
    assert "A sample repository for testing." in prompt
    assert "yourusername" in prompt or "no placeholder" in prompt
