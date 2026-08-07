from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.skills.security_skill import SecuritySkill


class SecurityAgent(BaseAgent):
    def __init__(self, database_service: DatabaseService) -> None:
        self.security_skill = SecuritySkill()
        self.database_service = database_service

    def handle(self, payload: dict) -> dict:
        repository_id = payload.get("repository_id")
        if not repository_id:
            return {"error": "Missing repository_id"}

        repo = self.database_service.get_repository(int(repository_id))
        if not repo or not repo.root_path:
            return {"security_score": 100.0, "issues": [], "recommendations": ["No repository files found to scan."]}

        findings = self.security_skill.scan_repository(repo.root_path)

        # Compute dynamic security score
        score = 100.0
        critical_count = 0
        high_count = 0
        medium_count = 0

        for f in findings:
            if f["severity"] == "CRITICAL":
                score -= 25.0
                critical_count += 1
            elif f["severity"] == "HIGH":
                score -= 15.0
                high_count += 1
            elif f["severity"] == "MEDIUM":
                score -= 5.0
                medium_count += 1

        score = max(0.0, score)

        # Update database health metrics with this new security score
        health = self.database_service.get_health_metrics(repo.id)
        current_scores = {
            "documentation_score": health.documentation_score if health else 70.0,
            "testing_score": health.testing_score if health else 60.0,
            "security_score": score,
            "maintainability_score": health.maintainability_score if health else 70.0,
            "complexity_score": health.complexity_score if health else 70.0,
        }
        current_scores["overall_score"] = round(sum(current_scores.values()) / 5)
        self.database_service.save_health_metrics(repo.id, current_scores)

        # Generate custom recommendations based on scan results
        recommendations = []
        if critical_count > 0:
            recommendations.append(
                f"CRITICAL: Found {critical_count} exposed credentials or secrets. Revoke them "
                "immediately and migrate to .env variables!"
            )
        if high_count > 0:
            recommendations.append(
                f"HIGH: Found {high_count} risky query or scripting methods (e.g. potential "
                "SQL Injection). Rewrite using parameter bindings."
            )
        if medium_count > 0:
            recommendations.append(
                f"MEDIUM: Found {medium_count} unsafe command execution modules (e.g. eval/exec). "
                "Replace with secure utility equivalents."
            )
        if not findings:
            recommendations.append("Excellent! No major security vulnerabilities or exposed secrets were detected.")

        return {"security_score": score, "issues": findings, "recommendations": recommendations}
