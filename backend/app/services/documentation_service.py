"""Documentation generation service with repo-grounded prompts and fallbacks."""

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.core.logger import get_logger

logger = get_logger(__name__)

# Fallback templates are grounded in the repository's real name and summary so
# offline generation still reflects the analyzed repo instead of generic filler.
_TEMPLATES: dict[str, str] = {
    "readme": (
        "# {title}\n\n"
        "## Overview\n\n{summary}\n\n"
        "## Repository structure\n\n"
        "This documentation was automatically generated for the repository with DevPilot AI.\n"
    ),
    "api": (
        "# API Reference\n\n"
        "## Endpoints\n\n"
        "Below is an index of the API surface identified in the repository "
        "(`{title}`). Refer to the source for exact request and response shapes.\n"
    ),
    "architecture": (
        "# Architecture\n\n"
        "## Overview\n\n{summary}\n\n"
        "This section summarizes the architectural structure of `{title}` as "
        "captured during repository analysis.\n"
    ),
    "install": (
        "# Installation\n\n"
        "## Prerequisites\n\n"
        "Check `requirements.txt` / `pyproject.toml` (or the equivalent manifest) "
        "for the exact dependency set of `{title}`.\n\n"
        "## Steps\n\n"
        "1. Clone the repository.\n"
        "2. Install dependencies from the project manifest.\n"
        "3. Run the application entry point documented in the README.\n"
    ),
    "contributing": (
        "# Contributing\n\n"
        "Contributions are welcome for `{title}`. Please open an issue or pull "
        "request and follow the repository's existing code style and tests.\n"
    ),
    "changelog": ("# Changelog\n\n## [Unreleased]\n\n- Initial analysis of `{title}` performed with DevPilot AI.\n"),
}


class DocumentationService:
    def __init__(self, llm: Any) -> None:
        self.llm = llm

    def generate(
        self,
        doc_types: list[str],
        target_files: list[str] | None = None,
        repository: Any = None,
    ) -> list[dict[str, str]]:
        repo_name = getattr(repository, "name", None) or "Repository"
        repo_summary = getattr(repository, "summary", None) or "No summary available for this repository."

        def _build(doc_type: str) -> dict[str, str]:
            key = doc_type.lower()
            title = self._title(repo_name, key)
            prompt = self._prompt(repo_name, repo_summary, key, target_files)
            return {
                "type": doc_type,
                "title": title,
                "content": self._generate(prompt, key, title=title, summary=repo_summary),
            }

        # LLM calls are I/O bound; generate selected docs in parallel so N docs
        # take roughly one call's latency instead of N calls back to back.
        workers = min(len(doc_types), 4)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(_build, doc_types))

    def _generate(self, prompt: str, doc_type: str, title: str, summary: str) -> str:
        try:
            if hasattr(self.llm, "generate_text"):
                content = self.llm.generate_text(prompt, timeout=60.0, max_tokens=1500)
            else:
                content = self.llm.generate(prompt, timeout=60.0, max_tokens=1500)
            if content and not content.startswith("LLM request failed"):
                return content
        except Exception as exc:  # graceful fallback per constitution
            logger.warning("Documentation generation via LLM failed (%s); using template", exc)
        template = _TEMPLATES.get(doc_type, _TEMPLATES["readme"])
        return template.format(title=title, summary=summary)

    @staticmethod
    def _title(repo_name: str, doc_type: str) -> str:
        label = {
            "readme": "README",
            "api": "API Reference",
            "architecture": "Architecture",
            "install": "Installation Guide",
            "contributing": "Contributing",
            "changelog": "Changelog",
        }.get(doc_type, doc_type.capitalize())
        return f"{repo_name} — {label}"

    @staticmethod
    def _prompt(repo_name: str, repo_summary: str, doc_type: str, target_files: list[str] | None) -> str:
        target = f" for files: {', '.join(target_files[:10])}" if target_files else ""
        return (
            f"Generate the {doc_type} documentation for the repository '{repo_name}'{target}.\n\n"
            f"Repository summary: {repo_summary}\n\n"
            "Requirements: use proper Markdown with headings, lists, and code blocks. "
            "Ground the content in the repository described above — no placeholder text, "
            "no generic filler, and never reference 'yourusername' or 'your-repo'."
        )
