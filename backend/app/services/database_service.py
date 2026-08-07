from typing import Any

from app.db.session import SessionLocal
from app.models.analysis_report import AnalysisReport
from app.models.repository import Repository


class DatabaseService:
    def create_repository(
        self, name: str, source_url: str | None = None, root_path: str | None = None, user_id: int | None = None
    ) -> Repository:
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

    def save_repository_files(self, repository_id: int, files: list) -> None:
        from app.models.repository_file import RepositoryFile

        with SessionLocal() as session:
            session.query(RepositoryFile).filter(RepositoryFile.repository_id == repository_id).delete()
            for f in files:
                db_file = RepositoryFile(
                    repository_id=repository_id,
                    file_path=f["file_path"],
                    language=f.get("language"),
                    file_type=f.get("file_type"),
                    checksum=f.get("checksum"),
                )
                session.add(db_file)
            session.commit()

    def get_repository_files(self, repository_id: int) -> list:
        from app.models.repository_file import RepositoryFile

        with SessionLocal() as session:
            return session.query(RepositoryFile).filter(RepositoryFile.repository_id == repository_id).all()

    def get_health_metrics(self, repository_id: int):
        from app.models.health_metric import HealthMetric

        with SessionLocal() as session:
            return (
                session.query(HealthMetric)
                .filter(HealthMetric.repository_id == repository_id)
                .order_by(HealthMetric.updated_at.desc())
                .first()
            )

    def save_health_metrics(self, repository_id: int, scores: dict) -> None:
        from app.models.health_metric import HealthMetric

        with SessionLocal() as session:
            metric = session.query(HealthMetric).filter(HealthMetric.repository_id == repository_id).first()
            if not metric:
                metric = HealthMetric(repository_id=repository_id)
            metric.documentation_score = scores.get("documentation_score", 0.0)
            metric.testing_score = scores.get("testing_score", 0.0)
            metric.security_score = scores.get("security_score", 0.0)
            metric.maintainability_score = scores.get("maintainability_score", 0.0)
            metric.complexity_score = scores.get("complexity_score", 0.0)
            metric.overall_score = scores.get("overall_score", 0.0)
            session.add(metric)
            session.commit()
