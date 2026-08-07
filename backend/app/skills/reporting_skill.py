from typing import Dict

class ReportingSkill:
    def compute_health_scores(self, metrics: Dict[str, float]) -> Dict[str, float]:
        documentation = metrics.get("documentation", 0)
        testing = metrics.get("testing", 0)
        security = metrics.get("security", 0)
        maintainability = metrics.get("maintainability", 0)
        complexity = metrics.get("complexity", 0)
        overall = round((documentation + testing + security + maintainability + complexity) / 5)
        return {
            "documentation_score": documentation,
            "testing_score": testing,
            "security_score": security,
            "maintainability_score": maintainability,
            "complexity_score": complexity,
            "overall_score": overall,
        }
