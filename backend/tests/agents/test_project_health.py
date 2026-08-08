"""Tests for the Project Health agent."""

from unittest.mock import MagicMock

from app.agents.project_health import ProjectHealthAgent
from app.services.database_service import DatabaseService

EXPECTED_SCORES = {
    "documentation_score": 72,
    "testing_score": 65,
    "security_score": 62,
    "maintainability_score": 70,
    "complexity_score": 68,
    "overall_score": 67,
}


def _agent(llm=None) -> tuple[ProjectHealthAgent, MagicMock]:
    db = MagicMock(spec=DatabaseService)
    repo = MagicMock()
    repo.id = 1
    repo.summary = "A repository summary"
    db.get_repository.return_value = repo
    return ProjectHealthAgent(db, llm=llm), db


def test_missing_repository_id_returns_error():
    agent, _ = _agent()
    assert agent.handle({}) == {"error": "Missing repository_id"}


def test_repository_not_found_returns_error():
    agent, db = _agent()
    db.get_repository.return_value = None
    assert agent.handle({"repository_id": "1"}) == {"error": "Repository not found"}


def test_computes_and_persists_scores():
    agent, db = _agent()

    result = agent.handle({"repository_id": "1"})

    for key, value in EXPECTED_SCORES.items():
        assert result[key] == value
    db.save_health_metrics.assert_called_once_with(1, {k: v for k, v in EXPECTED_SCORES.items()})


def test_rule_based_recommendations_when_scores_low():
    agent, _ = _agent()

    result = agent.handle({"repository_id": "1"})

    assert len(result["recommendations"]) == 4
    assert any("documentation" in r for r in result["recommendations"])
    assert any("testing" in r for r in result["recommendations"])
    assert any("security" in r for r in result["recommendations"])
    assert any("maintainability" in r for r in result["recommendations"])


def test_llm_bullets_appended_with_real_key():
    llm = MagicMock()
    llm.api_key = "real_key"
    llm.generate.return_value = "- Add CI coverage gate\n- Introduce type checks"
    agent, _ = _agent(llm=llm)

    result = agent.handle({"repository_id": "1"})

    assert "- Add CI coverage gate" in result["recommendations"]
    assert "- Introduce type checks" in result["recommendations"]


def test_llm_failure_keeps_rule_based_only():
    llm = MagicMock()
    llm.api_key = "real_key"
    llm.generate.return_value = "LLM request failed (429). Falling back to local rules."
    agent, _ = _agent(llm=llm)

    result = agent.handle({"repository_id": "1"})

    assert all(not r.startswith("-") for r in result["recommendations"])
