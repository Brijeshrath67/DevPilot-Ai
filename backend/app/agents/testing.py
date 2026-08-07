from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.services.testing_service import TestingService


class TestingAgent(BaseAgent):
    """Generates test scaffolds for the repository."""

    def __init__(self, testing_service: TestingService, database_service: DatabaseService) -> None:
        self.testing_service = testing_service
        self.database_service = database_service

    def handle(self, payload: dict) -> dict:
        test_types = payload.get("test_types", ["unit"])
        target_files = payload.get("target_files")
        repository_id = payload.get("repository_id")
        repository = self.database_service.get_repository(int(repository_id)) if repository_id else None
        if not repository:
            return {"error": "Repository not found"}

        tests = self.testing_service.generate(test_types, target_files)
        return {"tests": tests}
