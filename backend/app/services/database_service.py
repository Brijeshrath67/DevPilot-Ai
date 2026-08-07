from app.database.db import get_backend
from app.database.models import HealthMetricRecord, RepositoryFileRecord, RepositoryRecord


class DatabaseService:
    """Storage-agnostic repository for repositories, files, and health metrics."""

    def __init__(self) -> None:
        self.backend = get_backend()

    def create_repository(
        self, name: str, source_url: str | None = None, root_path: str | None = None, user_id: int | None = None
    ) -> RepositoryRecord:
        return self.backend.create_repository(name, source_url=source_url, root_path=root_path, user_id=user_id)

    def get_repository(self, repository_id: int) -> RepositoryRecord | None:
        return self.backend.get_repository(repository_id)

    def list_repositories(self) -> list[RepositoryRecord]:
        return self.backend.list_repositories()

    def save_analysis_report(self, repository_id: int, report_type: str, summary: dict) -> None:
        self.backend.save_analysis_report(repository_id, report_type, summary)

    def update_repository_summary(self, repository_id: int, summary: str, architecture_summary: str) -> None:
        self.backend.update_repository_summary(repository_id, summary, architecture_summary)

    def update_repository_root(self, repository_id: int, root_path: str) -> None:
        self.backend.update_repository_root(repository_id, root_path)

    def save_repository_files(self, repository_id: int, files: list) -> None:
        self.backend.save_repository_files(repository_id, files)

    def get_repository_files(self, repository_id: int) -> list[RepositoryFileRecord]:
        return self.backend.get_repository_files(repository_id)

    def get_health_metrics(self, repository_id: int) -> HealthMetricRecord | None:
        return self.backend.get_health_metrics(repository_id)

    def save_health_metrics(self, repository_id: int, scores: dict) -> None:
        self.backend.save_health_metrics(repository_id, scores)
