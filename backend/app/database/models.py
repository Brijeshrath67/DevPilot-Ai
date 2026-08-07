"""Data models.

Contains the SQLAlchemy ORM models used by the SQLite fallback backend and the
plain dataclass records returned by the MongoDB backend. Both expose the same
attributes so upstream services and agents do not care which store is active.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(UTC)


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    root_path = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    primary_language = Column(String, nullable=True)
    framework = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    architecture_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="repositories")
    files = relationship("RepositoryFile", back_populates="repository")
    analysis_reports = relationship("AnalysisReport", back_populates="repository")
    health_metrics = relationship("HealthMetric", back_populates="repository")
    chat_sessions = relationship("ChatSession", back_populates="repository")
    embedding_records = relationship("EmbeddingRecord", back_populates="repository")


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    report_type = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repository = relationship("Repository", back_populates="analysis_reports")


class RepositoryFile(Base):
    __tablename__ = "repository_files"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    file_path = Column(String, nullable=False)
    language = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    checksum = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repository = relationship("Repository", back_populates="files")


class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    documentation_score = Column(Float, default=0.0)
    testing_score = Column(Float, default=0.0)
    security_score = Column(Float, default=0.0)
    maintainability_score = Column(Float, default=0.0)
    complexity_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    repository = relationship("Repository", back_populates="health_metrics")


class EmbeddingRecord(Base):
    __tablename__ = "embedding_records"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    source_type = Column(String, nullable=False)
    source_id = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    vector_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repository = relationship("Repository", back_populates="embedding_records")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    github_id = Column(String, unique=True, nullable=True)
    auth_provider = Column(String, nullable=False, default="jwt")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repositories = relationship("Repository", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repository = relationship("Repository", back_populates="chat_sessions")
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="chat_session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat_session = relationship("ChatSession", back_populates="messages")


@dataclass
class RepositoryRecord:
    id: int
    name: str
    source_url: str | None = None
    root_path: str | None = None
    status: str = "created"
    summary: str | None = None
    architecture_summary: str | None = None
    primary_language: str | None = None
    framework: str | None = None
    user_id: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class RepositoryFileRecord:
    id: int
    file_path: str
    language: str | None = None
    file_type: str | None = None
    checksum: str | None = None
    repository_id: int = 0
    created_at: datetime | None = None


@dataclass
class HealthMetricRecord:
    repository_id: int
    documentation_score: float = 0.0
    testing_score: float = 0.0
    security_score: float = 0.0
    maintainability_score: float = 0.0
    complexity_score: float = 0.0
    overall_score: float = 0.0
    id: int | None = None
    updated_at: datetime | None = None


@dataclass
class Document:
    """Generic wrapper used by the MongoDB backend for one query row."""

    data: dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError(name) from None

    def __getitem__(self, name: str) -> Any:
        return self.data[name]

    def get(self, name: str, default: Any = None) -> Any:
        return self.data.get(name, default)
