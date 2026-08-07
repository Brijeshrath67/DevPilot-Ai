from app.db.base import Base
from app.db.session import engine
import app.models  # Register all models so they are created

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
