import os
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.services.parser_service import ParserService


class RepositoryAnalyzerAgent(BaseAgent):
    def __init__(self, parser_service: ParserService, database_service: DatabaseService):
        self.parser_service = parser_service
        self.database_service = database_service

    def handle(self, payload: dict) -> dict:
        repository_id = payload["repository_id"]
        analysis_scope = payload.get("analysis_scope", "full")

        summary = self.parser_service.analyze_repository(repository_id, scope=analysis_scope)
        self.database_service.save_analysis_report(int(repository_id), "repository_analysis", summary)
        self.database_service.update_repository_summary(
            int(repository_id),
            summary["project_summary"],
            summary["architecture_summary"],
        )

        # Index files in database and vector store for chat contextual QA
        repo = self.database_service.get_repository(int(repository_id))
        if repo and repo.root_path:
            root = Path(repo.root_path)
            db_files = []
            vector_items = []

            for path in root.rglob("*"):
                if path.is_file():
                    if any(
                        part in path.parts
                        for part in ["venv", ".venv", "node_modules", ".git", "__pycache__", "dist", "build"]
                    ):
                        continue

                    suffix = path.suffix.lower()
                    from app.services.parser_service import LANGUAGE_EXTENSIONS

                    language = LANGUAGE_EXTENSIONS.get(suffix, "Text")

                    relative_path = str(path.relative_to(root)).replace("\\", "/")
                    db_files.append(
                        {
                            "file_path": relative_path,
                            "language": language,
                            "file_type": "source_code"
                            if suffix in LANGUAGE_EXTENSIONS
                            else "documentation"
                            if suffix in [".md", ".txt"]
                            else "config",
                            "checksum": str(os.path.getsize(path)),
                        }
                    )

                    try:
                        content = path.read_text(encoding="utf-8", errors="ignore")
                        if len(content.strip()) > 10:
                            vector_items.append(
                                {
                                    "id": f"{repository_id}_{relative_path}",
                                    "vector": [0.0],
                                    "text": f"File: {relative_path}\nLanguage: {language}\nContent:\n{content[:2000]}",
                                    "metadata": {"repository_id": str(repository_id), "file_path": relative_path},
                                }
                            )
                    except Exception:  # noqa: S110  # best-effort indexing, skip unreadable files
                        pass

            if db_files:
                self.database_service.save_repository_files(repo.id, db_files)
            if vector_items:
                from app.services.vector_service import VectorService

                v_service = VectorService()
                v_service.upsert_vectors(vector_items)

        return {"analysis_id": repository_id, "summary": summary}
