import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.clients.config import config

def get_db() -> Session:
    DEBUG = int(os.environ.get("DEBUG", "0"))
    engine = create_engine(config.get("db-credentials"), echo=(DEBUG == 1))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
