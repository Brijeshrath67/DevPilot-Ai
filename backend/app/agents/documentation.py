from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.services.documentation_service import DocumentationService


class DocumentationAgent(BaseAgent):
    """Generates developer documentation for the repository."""

    def __init__(self, documentation_service: DocumentationService, database_service: DatabaseService) -> None:
        self.documentation_service = documentation_service
        self.database_service = database_service

    def handle(self, payload: dict) -> dict:
        doc_types = payload.get("doc_types", ["README"])
        target_files = payload.get("target_files")
        repository_id = payload.get("repository_id")
        repository = self.database_service.get_repository(int(repository_id)) if repository_id else None
        if not repository:
            return {"error": "Repository not found"}

        documents = self.documentation_service.generate(doc_types, target_files)
        return {"documents": documents}
