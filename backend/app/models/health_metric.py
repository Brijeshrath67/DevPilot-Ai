from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

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
