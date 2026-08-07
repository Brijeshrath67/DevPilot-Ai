from app.agents.base_agent import BaseAgent
from app.services.parser_service import ParserService
from app.services.database_service import DatabaseService

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

        return {"analysis_id": repository_id, "summary": summary}
