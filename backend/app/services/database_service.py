from typing import Any
from app.db.session import SessionLocal
from app.models.repository import Repository
from app.models.analysis_report import AnalysisReport

class DatabaseService:
    def create_repository(self, name: str, source_url: str | None = None, root_path: str | None = None, user_id: int | None = None) -> Repository:
        with SessionLocal() as session:
            repository = Repository(
                name=name,
                source_url=source_url,
                root_path=root_path,
                user_id=user_id or 1,
                status="created",
            )
            session.add(repository)
            session.commit()
            session.refresh(repository)
            return repository

    def get_repository(self, repository_id: int) -> Repository | None:
        with SessionLocal() as session:
            return session.get(Repository, repository_id)

    def save_analysis_report(self, repository_id: int, report_type: str, summary: Any) -> None:
        with SessionLocal() as session:
            report = AnalysisReport(
                repository_id=repository_id,
                report_type=report_type,
                summary=summary.get("project_summary", ""),
                details=str(summary),
            )
            session.add(report)
            session.commit()

    def update_repository_summary(self, repository_id: int, summary: str, architecture_summary: str) -> None:
        with SessionLocal() as session:
            repository = session.get(Repository, repository_id)
            if repository:
                repository.summary = summary
                repository.architecture_summary = architecture_summary
                repository.status = "analyzed"
                session.add(repository)
                session.commit()

    def update_repository_root(self, repository_id: int, root_path: str) -> None:
        with SessionLocal() as session:
            repository = session.get(Repository, repository_id)
            if repository:
                repository.root_path = root_path
                repository.status = "ingested"
                session.add(repository)
                session.commit()
