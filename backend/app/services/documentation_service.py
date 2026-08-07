"""Documentation generation service with deterministic fallback templates."""

from typing import Any

from app.core.logger import get_logger

logger = get_logger(__name__)

TEMPLATES = {
    "readme": "# {title}\n\nAutomatically generated README for the analyzed repository.\n\n"
    "## Overview\n\nThis repository was analyzed with DevPilot AI.\n",
    "readme.md": "# {title}\n\nAutomatically generated README for the analyzed repository.\n",
    "api": "# API Reference\n\nGenerated API reference for the repository's endpoints.\n",
    "architecture": "# Architecture\n\nGenerated architecture overview.\n",
    "install": "# Installation\n\n1. Clone the repository\n2. Install dependencies\n3. Run the application\n",
    "contributing": "# Contributing\n\nContributions are welcome.\n",
    "changelog": "# Changelog\n\n## [1.0.0] - Initial release\n",
}


class DocumentationService:
    def __init__(self, llm: Any) -> None:
        self.llm = llm

    def generate(self, doc_types: list[str], target_files: list[str] | None = None) -> list[dict[str, str]]:
        documents = []
        for doc_type in doc_types:
            target = ""
            if target_files:
                target = f" for files: {', '.join(target_files[:10])}"
            prompt = f"Generate {doc_type} documentation{target} for the repository."
            documents.append({"type": doc_type, "content": self._generate(prompt, doc_type)})
        return documents

    def _generate(self, prompt: str, doc_type: str) -> str:
        try:
            if hasattr(self.llm, "generate_text"):
                content = self.llm.generate_text(prompt)
            else:
                content = self.llm.generate(prompt)
            if content and not content.startswith("LLM request failed"):
                return content
        except Exception as exc:  # noqa: BLE001  # graceful fallback per constitution
            logger.warning("Documentation generation via LLM failed (%s); using template", exc)
        template = TEMPLATES.get(doc_type.lower(), TEMPLATES["readme"])
        return template.format(title=doc_type.capitalize())
