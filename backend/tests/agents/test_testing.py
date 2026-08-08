"""Tests for the Testing agent."""

from unittest.mock import MagicMock

from app.agents.testing import TestingAgent
from app.services.database_service import DatabaseService
from app.services.testing_service import TestingService


def _agent(llm=None) -> tuple[TestingAgent, MagicMock]:
    db = MagicMock(spec=DatabaseService)
    repo = MagicMock()
    repo.id = 1
    db.get_repository.return_value = repo
    return TestingAgent(TestingService(llm), db), db


def test_missing_repository_returns_error():
    db = MagicMock(spec=DatabaseService)
    db.get_repository.return_value = None
    agent = TestingAgent(TestingService(None), db)
    assert agent.handle({"repository_id": "1"}) == {"error": "Repository not found"}


def test_defaults_to_unit():
    agent, _ = _agent(llm=None)
    result = agent.handle({"repository_id": "1"})
    expected = (
        "import pytest\n\n"
        "def test_addition():\n    assert add(2, 3) == 5\n\n"
        "def test_subtraction():\n    assert subtract(5, 3) == 2\n"
    )
    assert result["tests"] == [{"type": "unit", "content": expected}]


def test_generates_requested_test_types():
    llm = MagicMock(spec=["generate"])
    llm.generate.return_value = "def test_ok(): pass"
    agent, _ = _agent(llm=llm)

    result = agent.handle({"repository_id": "1", "test_types": ["unit", "integration"]})

    assert {t["type"] for t in result["tests"]} == {"unit", "integration"}
    assert result["tests"][0]["content"] == "def test_ok(): pass"


def test_passes_target_files_to_service():
    llm = MagicMock(spec=["generate"])
    llm.generate.return_value = "content"
    agent, _ = _agent(llm=llm)

    agent.handle({"repository_id": "1", "test_types": ["unit"], "target_files": ["app/services/llm_service.py"]})

    prompt = llm.generate.call_args[0][0]
    assert "app/services/llm_service.py" in prompt


def test_falls_back_to_template_when_llm_fails():
    llm = MagicMock(spec=["generate"])
    llm.generate.return_value = "LLM request failed (timeout). Falling back to local rules."
    agent, _ = _agent(llm=llm)

    result = agent.handle({"repository_id": "1", "test_types": ["unit"]})

    assert "import pytest" in result["tests"][0]["content"]
