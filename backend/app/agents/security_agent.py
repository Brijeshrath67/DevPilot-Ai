from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.skills.security_skill import SecuritySkill


class SecurityAgent(BaseAgent):
    """Dedicated security scanner using the security skill's pattern dictionary."""

    def __init__(self, database_service: DatabaseService) -> None:
        self.database_service = database_service
        self.security_skill = SecuritySkill()

    def handle(self, payload: dict) -> dict:
        repository_id = payload.get("repository_id")
        repository = self.database_service.get_repository(int(repository_id)) if repository_id else None
        if not repository:
            return {"security_score": 100.0, "issues": [], "recommendations": []}

        issues = self.security_skill.scan_repository(repository.root_path or "") if repository.root_path else []

        severity_weights = {"CRITICAL": 30, "HIGH": 15, "MEDIUM": 5, "MINOR": 1}
        security_score = max(0, 100 - sum(severity_weights.get(i.get("severity", "MINOR"), 1) for i in issues))

        recommendations = [
            f"CRITICAL - {i['vulnerability']} at {i['file']}:{i['line']} - {i['recommendation']}"
            for i in issues
            if i.get("severity") == "CRITICAL"
        ] + [
            f"HIGH - {i['vulnerability']} at {i['file']}:{i['line']} - {i['recommendation']}"
            for i in issues
            if i.get("severity") == "HIGH"
        ]

        return {
            "security_score": float(security_score),
            "issues": issues,
            "recommendations": recommendations,
        }
