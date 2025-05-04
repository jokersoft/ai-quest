import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.clients.config import config

def get_db() -> Session:
    DEBUG = int(os.environ.get("DEBUG", "0"))
    # Retrieve the DATABASE_URL from environment variables
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    engine = create_engine(database_url, echo=(DEBUG == 1))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
