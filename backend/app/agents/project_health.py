from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.services.health_service import HealthService
from app.skills.reporting_skill import ReportingSkill


class ProjectHealthAgent(BaseAgent):
    """Computes health scores; uses the routed LLM (Cerebras) for insights."""

    def __init__(self, database_service: DatabaseService, llm: Any = None) -> None:
        self.database_service = database_service
        self.llm = llm
        self.health_service = HealthService()
        self.reporting_skill = ReportingSkill()

    def handle(self, payload: dict) -> dict:
        repository_id = payload.get("repository_id")
        if not repository_id:
            return {"error": "Missing repository_id"}
        repository = self.database_service.get_repository(int(repository_id))
        if not repository:
            return {"error": "Repository not found"}

        metrics = self.health_service.compute_health_metrics(repository.summary)
        scores = self.reporting_skill.compute_health_scores(metrics)
        self.database_service.save_health_metrics(repository.id, scores)

        recommendations = self._recommendations(scores)
        return {**scores, "recommendations": recommendations}

    def _recommendations(self, scores: dict[str, float]) -> list[str]:
        rule_based = []
        if scores["documentation_score"] < 75:
            rule_based.append("Add API and architecture documentation to raise the documentation score.")
        if scores["testing_score"] < 75:
            rule_based.append("Increase test coverage with unit and integration tests to raise the testing score.")
        if scores["security_score"] < 75:
            rule_based.append("Resolve CRITICAL/HIGH security findings before deploying to production.")
        if scores["maintainability_score"] < 75:
            rule_based.append("Refactor long functions and duplicated logic to improve maintainability.")

        if self.llm is None or not getattr(self.llm, "api_key", None) or self.llm.api_key in {"", "mock_key"}:
            return rule_based

        prompt = (
            f"The project health scores are: documentation={scores['documentation_score']}, "
            f"testing={scores['testing_score']}, security={scores['security_score']}, "
            f"maintainability={scores['maintainability_score']}, complexity={scores['complexity_score']}. "
            "Suggest 3 concrete improvements, one short bullet per line."
        )
        content = self.llm.generate(prompt, temperature=0.2, max_tokens=200)
        if content and not content.startswith("LLM request failed"):
            return rule_based + [line.strip() for line in content.splitlines() if line.strip()]
        return rule_based
