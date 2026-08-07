"""Database connections and storage backends.

Two backends are supported:

* ``MongoStorageBackend`` — used when ``MONGODB_URI`` is configured (MongoDB Atlas).
* ``SqlStorageBackend`` — SQLAlchemy/SQLite fallback used when MongoDB is
  unavailable, so the application keeps working without external secrets.

``get_backend()`` returns the active backend and always degrades gracefully.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logger import get_logger
from app.database.models import (
    AnalysisReport,
    Base,
    HealthMetric,
    HealthMetricRecord,
    Repository,
    RepositoryFile,
    RepositoryFileRecord,
    RepositoryRecord,
    utcnow,
)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# SQLite / SQLAlchemy connection
# ---------------------------------------------------------------------------

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# MongoDB connection (lazy) with graceful fallback
# ---------------------------------------------------------------------------

_mongo_client: Any = None
_mongo_database: Any = None


def _connect_mongodb() -> Any:
    """Return the MongoDB database handle or None if it cannot be reached."""
    global _mongo_client, _mongo_database
    if not settings.use_mongodb:
        return None
    if _mongo_database is not None:
        return _mongo_database
    try:
        from pymongo import MongoClient

        client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=4000)
        client.admin.command("ping")
        _mongo_client = client
        _mongo_database = client[settings.mongodb_db_name]
        logger.info("Connected to MongoDB Atlas database '%s'", settings.mongodb_db_name)
        return _mongo_database
    except Exception as exc:  # pragma: no cover - graceful fallback path
        logger.warning("MongoDB unavailable (%s); falling back to SQLite", exc)
        return None


def get_collection(name: str) -> Any:
    db = _connect_mongodb()
    if db is None:
        raise RuntimeError("MongoDB is not configured or unreachable")
    return db[name]


def _next_sequence(name: str) -> int:
    counters = get_collection("counters")
    result = counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return result["seq"]


# ---------------------------------------------------------------------------
# Backends
# ---------------------------------------------------------------------------


class SqlStorageBackend:
    """SQLite/SQLAlchemy implementation of the storage interface."""

    def create_repository(self, name, source_url=None, root_path=None, user_id=None) -> RepositoryRecord:
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
            return RepositoryRecord(
                id=repository.id,
                name=repository.name,
                source_url=repository.source_url,
                root_path=repository.root_path,
                status=repository.status,
                user_id=repository.user_id,
                created_at=repository.created_at,
            )

    def get_repository(self, repository_id: int) -> RepositoryRecord | None:
        with SessionLocal() as session:
            repository = session.get(Repository, repository_id)
            if not repository:
                return None
            return RepositoryRecord(
                id=repository.id,
                name=repository.name,
                source_url=repository.source_url,
                root_path=repository.root_path,
                status=repository.status,
                summary=repository.summary,
                architecture_summary=repository.architecture_summary,
                primary_language=repository.primary_language,
                framework=repository.framework,
                user_id=repository.user_id,
                created_at=repository.created_at,
            )

    def list_repositories(self) -> list[RepositoryRecord]:
        with SessionLocal() as session:
            rows = session.query(Repository).order_by(Repository.id.desc()).all()
            return [self.get_repository(row.id) for row in rows if row.id is not None]

    def save_analysis_report(self, repository_id: int, report_type: str, summary: dict) -> None:
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

    def get_repository_files(self, repository_id: int) -> list[RepositoryFileRecord]:
        with SessionLocal() as session:
            rows = session.query(RepositoryFile).filter(RepositoryFile.repository_id == repository_id).all()
            return [
                RepositoryFileRecord(
                    id=f.id,
                    repository_id=f.repository_id,
                    file_path=f.file_path,
                    language=f.language,
                    file_type=f.file_type,
                    checksum=f.checksum,
                )
                for f in rows
            ]

    def get_health_metrics(self, repository_id: int) -> HealthMetricRecord | None:
        with SessionLocal() as session:
            metric = (
                session.query(HealthMetric)
                .filter(HealthMetric.repository_id == repository_id)
                .order_by(HealthMetric.updated_at.desc())
                .first()
            )
            if not metric:
                return None
            return HealthMetricRecord(
                id=metric.id,
                repository_id=metric.repository_id,
                documentation_score=metric.documentation_score,
                testing_score=metric.testing_score,
                security_score=metric.security_score,
                maintainability_score=metric.maintainability_score,
                complexity_score=metric.complexity_score,
                overall_score=metric.overall_score,
                updated_at=metric.updated_at,
            )

    def save_health_metrics(self, repository_id: int, scores: dict) -> None:
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


class MongoStorageBackend:
    """MongoDB (Atlas) implementation of the storage interface."""

    def __init__(self) -> None:
        self.db = _connect_mongodb()
        if self.db is None:
            raise RuntimeError("MongoDB unavailable")

    def create_repository(self, name, source_url=None, root_path=None, user_id=None) -> RepositoryRecord:
        collection = get_collection("repositories")
        repo_id = _next_sequence("repositories")
        now = utcnow()
        document = {
            "_id": repo_id,
            "user_id": user_id or 1,
            "name": name,
            "source_url": source_url,
            "root_path": root_path,
            "status": "created",
            "primary_language": None,
            "framework": None,
            "summary": None,
            "architecture_summary": None,
            "created_at": now,
            "updated_at": now,
        }
        collection.insert_one(document)
        return RepositoryRecord(
            id=repo_id,
            name=name,
            source_url=source_url,
            root_path=root_path,
            status="created",
            user_id=user_id or 1,
            created_at=now,
        )

    def get_repository(self, repository_id: int) -> RepositoryRecord | None:
        doc = get_collection("repositories").find_one({"_id": repository_id})
        if not doc:
            return None
        return RepositoryRecord(
            id=doc["_id"],
            name=doc.get("name", ""),
            source_url=doc.get("source_url"),
            root_path=doc.get("root_path"),
            status=doc.get("status", "created"),
            summary=doc.get("summary"),
            architecture_summary=doc.get("architecture_summary"),
            primary_language=doc.get("primary_language"),
            framework=doc.get("framework"),
            user_id=doc.get("user_id", 1),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    def list_repositories(self) -> list[RepositoryRecord]:
        cursor = get_collection("repositories").find().sort("_id", -1)
        return [self._to_repository(doc) for doc in cursor]

    def _to_repository(self, doc: dict) -> RepositoryRecord:
        return RepositoryRecord(
            id=doc["_id"],
            name=doc.get("name", ""),
            source_url=doc.get("source_url"),
            root_path=doc.get("root_path"),
            status=doc.get("status", "created"),
            summary=doc.get("summary"),
            architecture_summary=doc.get("architecture_summary"),
            primary_language=doc.get("primary_language"),
            framework=doc.get("framework"),
            user_id=doc.get("user_id", 1),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    def save_analysis_report(self, repository_id: int, report_type: str, summary: dict) -> None:
        get_collection("analysis_reports").insert_one(
            {
                "_id": _next_sequence("analysis_reports"),
                "repository_id": repository_id,
                "report_type": report_type,
                "summary": summary.get("project_summary", ""),
                "details": str(summary),
                "created_at": utcnow(),
            }
        )

    def update_repository_summary(self, repository_id: int, summary: str, architecture_summary: str) -> None:
        get_collection("repositories").update_one(
            {"_id": repository_id},
            {
                "$set": {
                    "summary": summary,
                    "architecture_summary": architecture_summary,
                    "status": "analyzed",
                    "updated_at": utcnow(),
                }
            },
        )

    def update_repository_root(self, repository_id: int, root_path: str) -> None:
        get_collection("repositories").update_one(
            {"_id": repository_id},
            {"$set": {"root_path": root_path, "status": "ingested", "updated_at": utcnow()}},
        )

    def save_repository_files(self, repository_id: int, files: list) -> None:
        collection = get_collection("repository_files")
        collection.delete_many({"repository_id": repository_id})
        documents = []
        for f in files:
            documents.append(
                {
                    "repository_id": repository_id,
                    "file_path": f["file_path"],
                    "language": f.get("language"),
                    "file_type": f.get("file_type"),
                    "checksum": f.get("checksum"),
                    "created_at": utcnow(),
                }
            )
        if documents:
            collection.insert_many(documents)

    def get_repository_files(self, repository_id: int) -> list[RepositoryFileRecord]:
        cursor = get_collection("repository_files").find({"repository_id": repository_id})
        return [
            RepositoryFileRecord(
                id=str(doc["_id"]),
                repository_id=repository_id,
                file_path=doc["file_path"],
                language=doc.get("language"),
                file_type=doc.get("file_type"),
                checksum=doc.get("checksum"),
            )
            for doc in cursor
        ]

    def get_health_metrics(self, repository_id: int) -> HealthMetricRecord | None:
        doc = get_collection("health_metrics").find_one({"repository_id": repository_id})
        if not doc:
            return None
        return HealthMetricRecord(
            id=str(doc.get("_id")),
            repository_id=repository_id,
            documentation_score=doc.get("documentation_score", 0.0),
            testing_score=doc.get("testing_score", 0.0),
            security_score=doc.get("security_score", 0.0),
            maintainability_score=doc.get("maintainability_score", 0.0),
            complexity_score=doc.get("complexity_score", 0.0),
            overall_score=doc.get("overall_score", 0.0),
            updated_at=doc.get("updated_at"),
        )

    def save_health_metrics(self, repository_id: int, scores: dict) -> None:
        collection = get_collection("health_metrics")
        collection.update_one(
            {"repository_id": repository_id},
            {
                "$set": {
                    "documentation_score": scores.get("documentation_score", 0.0),
                    "testing_score": scores.get("testing_score", 0.0),
                    "security_score": scores.get("security_score", 0.0),
                    "maintainability_score": scores.get("maintainability_score", 0.0),
                    "complexity_score": scores.get("complexity_score", 0.0),
                    "overall_score": scores.get("overall_score", 0.0),
                    "updated_at": utcnow(),
                }
            },
            upsert=True,
        )


def get_backend() -> Any:
    """Return the active storage backend, degrading to SQLite if needed."""
    if settings.use_mongodb:
        try:
            return MongoStorageBackend()
        except Exception as exc:  # pragma: no cover - graceful fallback path
            logger.warning("Falling back to SQLite storage: %s", exc)
    init_db()
    return SqlStorageBackend()
