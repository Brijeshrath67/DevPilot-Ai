"""Report assembly service used by agents to shape structured responses."""

from app.skills.reporting_skill import ReportingSkill


class ReportService:
    def __init__(self) -> None:
        self.reporting_skill = ReportingSkill()

    def health_scores(self, metrics: dict[str, float]) -> dict[str, float]:
        return self.reporting_skill.compute_health_scores(metrics)

    def summarize_findings(self, issues: list[dict]) -> dict:
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "MINOR": 0}
        for issue in issues:
            severity = (issue.get("severity") or "MINOR").upper()
            counts[severity] = counts.get(severity, 0) + 1
        return {
            "total": len(issues),
            "by_severity": counts,
            "critical_count": counts["CRITICAL"],
            "high_count": counts["HIGH"],
        }
