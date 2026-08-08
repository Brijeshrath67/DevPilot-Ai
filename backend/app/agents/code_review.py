from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.skills.quality_skill import QualitySkill
from app.skills.security_skill import SecuritySkill


class CodeReviewAgent(BaseAgent):
    """Review agent: static security + code-quality scan (rule-based) + LLM review.

    The rule-based scans (security and maintainability) always run against the
    repository's actual files. When a real provider key is configured, the
    routed LLM adds a qualitative review pass; otherwise the rule-based
    findings are the review output. ``review_scope=changes`` limits the scan to
    files changed since HEAD when the repository is a git checkout.
    """

    def __init__(self, database_service: DatabaseService, llm: Any = None) -> None:
        self.database_service = database_service
        self.llm = llm
        self.security_skill = SecuritySkill()
        self.quality_skill = QualitySkill()

    def handle(self, payload: dict) -> dict:
        repository_id = payload.get("repository_id")
        repository = self.database_service.get_repository(int(repository_id)) if repository_id else None
        if not repository:
            return {"error": "Repository not found"}

        root_path = repository.root_path or ""
        scope = payload.get("review_scope", "full")
        target_files = self.resolve_scope_files(root_path, scope)

        security_issues = self.security_skill.scan_repository(root_path, files=target_files) if root_path else []
        quality_issues = self.quality_skill.scan_repository(root_path, files=target_files) if root_path else []
        issues = security_issues + quality_issues

        recommendations = [self._recommendation(i) for i in issues if i.get("severity") in {"CRITICAL", "HIGH"}]
        if target_files:
            recommendations.append(
                f"Review scope: {len(target_files)} file(s) changed since HEAD were reviewed "
                f"({', '.join(target_files[:5])}{'…' if len(target_files) > 5 else ''})."
            )

        llm_review = self._llm_review(
            repository.name,
            root_path,
            scope=scope,
            files=payload.get("files"),
        )
        if llm_review:
            recommendations.append(f"LLM review ({self._provider_name()}): {llm_review}")

        severity_weights = {"CRITICAL": 30, "HIGH": 15, "MEDIUM": 5, "MINOR": 1}
        security_score = max(0, 100 - sum(severity_weights.get(i.get("severity", "MINOR"), 1) for i in issues))

        return {
            "security_score": float(security_score),
            "issues": issues,
            "recommendations": recommendations,
        }

    def _llm_review(self, name: str, root_path: str, scope: str = "full", files: list[str] | None = None) -> str | None:
        if self.llm is None or not getattr(self.llm, "api_key", None) or self.llm.api_key in {"", "mock_key"}:
            return None
        target = f", focusing on files: {', '.join(files[:10])}" if files else ""
        prompt = (
            f"Perform a focused code review of the repository '{name}' at '{root_path}'"
            f" (scope: {scope}{target}). "
            "List the top 3 maintainability or correctness concerns in one or two sentences each."
        )
        content = self.llm.generate(prompt, temperature=0.2, max_tokens=200)
        if content and content.startswith("LLM request failed"):
            return None
        return content

    def _provider_name(self) -> str:
        return getattr(self.llm, "provider", "huggingface") if self.llm else "huggingface"

    @staticmethod
    def _recommendation(issue: dict) -> str:
        severity = issue.get("severity", "MINOR")
        return (
            f"{severity} - {issue.get('vulnerability', 'Issue')} at "
            f"{issue.get('file', '?')}:{issue.get('line', '?')} - {issue.get('recommendation', '')}"
        )
