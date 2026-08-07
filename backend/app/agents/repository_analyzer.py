from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.constants import IGNORED_DIRECTORIES, LANGUAGE_EXTENSIONS
from app.services.database_service import DatabaseService
from app.services.parser_service import ParserService
from app.utils.helpers import sha256_checksum


class RepositoryAnalyzerAgent(BaseAgent):
    """Analyzes repository structure, indexes files and persists summaries.

    Uses the routed LLM (default: Groq) to write the project summary when a
    real API key is configured, falling back to rule-based parsing otherwise.
    """

    def __init__(self, parser_service: ParserService, database_service: DatabaseService, llm: Any = None) -> None:
        self.parser_service = parser_service
        self.database_service = database_service
        self.llm = llm

    def handle(self, payload: dict) -> dict:
        repository_id = payload.get("repository_id")
        if not repository_id:
            return {"error": "Missing repository_id"}
        repository = self.database_service.get_repository(int(repository_id))
        if not repository:
            return {"error": "Repository not found"}

        result = self.parser_service.analyze_repository(str(repository_id), scope=payload.get("analysis_scope", "full"))

        if repository.root_path and Path(repository.root_path).is_dir():
            files = self._index_files(Path(repository.root_path))
            self.database_service.save_repository_files(repository.id, files)

        self.database_service.save_analysis_report(repository.id, "repository_analysis", result)
        self.database_service.update_repository_summary(
            repository.id, result["project_summary"], result["architecture_summary"]
        )

        return {
            "repository_id": repository.id,
            "summary": {
                "project_summary": self._enhance_summary(repository.name, result),
                "architecture_summary": result["architecture_summary"],
                "languages": result["languages"],
                "frameworks": result["frameworks"],
                "dependencies": result["dependencies"],
            },
        }

    def _enhance_summary(self, name: str, result: dict) -> str:
        """Ask the routed LLM for a richer summary when a real key is present."""
        if self.llm is None or not getattr(self.llm, "api_key", None) or self.llm.api_key in {"", "mock_key"}:
            return result["project_summary"]
        prompt = (
            f"Write a 2-3 sentence project summary for '{name}'. "
            f"Languages: {result['languages']}. Frameworks: {result['frameworks']}. "
            f"Dependencies: {result['dependencies']}."
        )
        return self.llm.generate(prompt, temperature=0.2, max_tokens=160)

    def _index_files(self, root_path: Path) -> list[dict]:
        source_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".java"}
        files = []
        for path in root_path.rglob("*"):
            if path.is_file() and not any(part in path.parts for part in IGNORED_DIRECTORIES):
                files.append(
                    {
                        "file_path": str(path.relative_to(root_path)).replace("\\", "/"),
                        "language": LANGUAGE_EXTENSIONS.get(path.suffix),
                        "file_type": "source" if path.suffix in source_extensions else "file",
                        "checksum": sha256_checksum(path.read_text(encoding="utf-8", errors="ignore")),
                    }
                )
        return files
