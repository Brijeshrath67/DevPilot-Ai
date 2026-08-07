from app.agents.base_agent import BaseAgent
from app.skills.reporting_skill import ReportingSkill

class ProjectHealthAgent(BaseAgent):
    def __init__(self) -> None:
        self.reporting_skill = ReportingSkill()

    def handle(self, payload: dict) -> dict:
        metrics = {
            "documentation": 72,
            "testing": 65,
            "security": 62,
            "maintainability": 70,
            "complexity": 68,
        }
        scores = self.reporting_skill.compute_health_scores(metrics)
        return {
            **scores,
            "recommendations": [
                "Increase unit test coverage for complex modules.",
                "Add architecture documentation for new contributors.",
            ],
        }
