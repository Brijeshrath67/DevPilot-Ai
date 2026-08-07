import app.models  # noqa: F401  # Register all models so they are created
from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
