from sqlalchemy.orm import relationship

from app.models.user import User
from app.models.repository import Repository
from app.models.repository_file import RepositoryFile
from app.models.analysis_report import AnalysisReport
from app.models.health_metric import HealthMetric
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.embedding_record import EmbeddingRecord

User.repositories = relationship("Repository", back_populates="user")
Repository.files = relationship("RepositoryFile", back_populates="repository")
Repository.analysis_reports = relationship("AnalysisReport", back_populates="repository")
Repository.health_metrics = relationship("HealthMetric", back_populates="repository")
Repository.chat_sessions = relationship("ChatSession", back_populates="repository")
Repository.embedding_records = relationship("EmbeddingRecord", back_populates="repository")
ChatSession.messages = relationship("ChatMessage", back_populates="chat_session")
User.chat_sessions = relationship("ChatSession", back_populates="user")
