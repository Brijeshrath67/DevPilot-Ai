"""Model registry.

Imports every ORM model so SQLAlchemy metadata is complete before
``Base.metadata.create_all`` runs. The unused-import hints are intentional:
each import registers the mapped table on the shared metadata.
"""

from sqlalchemy.orm import relationship

from app.models.analysis_report import AnalysisReport  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.chat_session import ChatSession  # noqa: F401
from app.models.embedding_record import EmbeddingRecord  # noqa: F401
from app.models.health_metric import HealthMetric  # noqa: F401
from app.models.repository import Repository  # noqa: F401
from app.models.repository_file import RepositoryFile  # noqa: F401
from app.models.user import User  # noqa: F401

User.repositories = relationship("Repository", back_populates="user")
Repository.files = relationship("RepositoryFile", back_populates="repository")
Repository.analysis_reports = relationship("AnalysisReport", back_populates="repository")
Repository.health_metrics = relationship("HealthMetric", back_populates="repository")
Repository.chat_sessions = relationship("ChatSession", back_populates="repository")
Repository.embedding_records = relationship("EmbeddingRecord", back_populates="repository")
ChatSession.messages = relationship("ChatMessage", back_populates="chat_session")
User.chat_sessions = relationship("ChatSession", back_populates="user")
