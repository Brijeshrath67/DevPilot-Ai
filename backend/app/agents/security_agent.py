import time

from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.skills.security_skill import SecuritySkill


class SecurityAgent(BaseAgent):
    """Dedicated security scanner using the security skill's pattern dictionary.

    Rule-based, runs in real time against the repository's actual files and
    returns scan metadata (files scanned, patterns checked) so the audit is
    verifiably grounded in the repository. ``review_scope=changes`` limits the
    audit to files changed since HEAD when the repository is a git checkout.
    """

    def __init__(self, database_service: DatabaseService) -> None:
        self.database_service = database_service
        self.security_skill = SecuritySkill()

    def handle(self, payload: dict) -> dict:
        repository_id = payload.get("repository_id")
        repository = self.database_service.get_repository(int(repository_id)) if repository_id else None
        if not repository:
            return {"security_score": 100.0, "issues": [], "recommendations": []}

        root_path = repository.root_path or ""
        explicit_files = payload.get("files") or None
        if explicit_files:
            target_files = explicit_files
        else:
            target_files = self.resolve_scope_files(root_path, payload.get("review_scope", "full"))

        start = time.perf_counter()
        result = self.security_skill.scan_repository_with_meta(root_path, files=target_files) if root_path else {}
        scan_time_ms = int((time.perf_counter() - start) * 1000)

        issues = result.get("findings", [])

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
        if target_files:
            recommendations.append(
                f"Audit scope: {len(target_files)} file(s) changed since HEAD were scanned "
                f"({', '.join(target_files[:5])}{'…' if len(target_files) > 5 else ''})."
            )

        return {
            "security_score": float(security_score),
            "issues": issues,
            "recommendations": recommendations,
            "files_scanned": result.get("files_scanned", 0),
            "patterns_checked": result.get("patterns_checked", self.security_skill.patterns_checked),
            "scan_time_ms": scan_time_ms,
        }
