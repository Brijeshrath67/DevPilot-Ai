import json

from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService


class CodeReviewAgent(BaseAgent):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def handle(self, payload: dict) -> dict:
        review_scope = payload.get("review_scope", "full")
        files = payload.get("files") or []
        target = ", ".join(files) if files else "the whole repository"
        raw = self.llm_service.generate(
            f"Review the code in scope {review_scope} for {target}. "
            "Return issues with severity, file, line, vulnerability, description and recommendation."
        )

        issues: list[dict] = []
        recommendations: list[str] = []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                issues = parsed.get("issues") or []
                recommendations = parsed.get("recommendations") or []
        except (json.JSONDecodeError, TypeError):
            issues = [
                {
                    "severity": "MEDIUM",
                    "file": "repository",
                    "line": 0,
                    "vulnerability": "Review completed with degraded output",
                    "description": "The reviewer could not produce a structured finding; raw output was captured.",
                    "recommendation": "Re-run the review with a configured AI provider for richer analysis.",
                }
            ]

        return {"issues": issues, "recommendations": recommendations, "review_scope": review_scope}
