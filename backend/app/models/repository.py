from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


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
