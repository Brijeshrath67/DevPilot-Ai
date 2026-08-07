"""Unit tests for agent orchestration and individual agents."""

from unittest.mock import MagicMock

from app.agents.base_agent import BaseAgent
from app.agents.orchestrator import AgentOrchestrator
from app.agents.project_health import ProjectHealthAgent
from app.agents.security_agent import SecurityAgent


def test_orchestrator_routes_to_registered_agent():
    orchestrator = AgentOrchestrator(
        llm_service=MagicMock(),
        parser_service=MagicMock(),
        embedding_service=MagicMock(),
        vector_service=MagicMock(),
        github_service=MagicMock(),
        database_service=MagicMock(),
    )
    captured = {}

    class FakeAgent(BaseAgent):
        def handle(self, payload: dict) -> dict:
            captured.update(payload)
            return {"ok": True}

    orchestrator.register_agent("fake", FakeAgent())
    result = orchestrator.route("fake", {"key": "value"})
    assert result == {"ok": True}
    assert captured == {"key": "value"}


def test_orchestrator_raises_for_unknown_agent():
    orchestrator = AgentOrchestrator(
        llm_service=MagicMock(),
        parser_service=MagicMock(),
        embedding_service=MagicMock(),
        vector_service=MagicMock(),
        github_service=MagicMock(),
        database_service=MagicMock(),
    )
    try:
        orchestrator.route("does_not_exist", {})
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_security_agent_returns_100_when_no_repo():
    database_service = MagicMock()
    database_service.get_repository.return_value = None
    agent = SecurityAgent(database_service)
    result = agent.handle({"repository_id": "1"})
    assert result["security_score"] == 100.0


def test_project_health_agent_requires_repository_id():
    agent = ProjectHealthAgent(MagicMock())
    assert agent.handle({})["error"] == "Missing repository_id"


def test_project_health_agent_missing_repo():
    database_service = MagicMock()
    database_service.get_repository.return_value = None
    agent = ProjectHealthAgent(database_service)
    result = agent.handle({"repository_id": "1"})
    assert result["error"] == "Repository not found"
