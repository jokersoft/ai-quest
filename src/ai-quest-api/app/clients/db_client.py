from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.clients import config

config = config.Config()


def get_db() -> Session:
    engine = create_engine(config.database_url, echo=(config.debug == 1))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
