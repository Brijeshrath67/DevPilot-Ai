from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    github_id = Column(String, unique=True, nullable=True)
    auth_provider = Column(String, nullable=False, default="jwt")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
