import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


def get_db() -> Session:
    DEBUG = int(os.environ.get("DEBUG", "0"))
    config = json.loads(os.environ["CONFIG"])
    engine = create_engine(config["db-credentials"], echo=(DEBUG == 1))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
