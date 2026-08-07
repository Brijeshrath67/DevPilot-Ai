from typing import Dict

class HealthService:
    def compute_health_metrics(self, repository_summary: str | None = None) -> Dict[str, int]:
        return {
            "documentation": 72,
            "testing": 65,
            "security": 62,
            "maintainability": 70,
            "complexity": 68,
        }
