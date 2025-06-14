import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.clients import config

config = config.Config()


def get_db() -> Session:
    engine = create_engine(config.database_url, echo=(config.debug == 1))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    return db


@contextlib.contextmanager
def session():
    """
    A context manager that yields a database connection and cleans up after itself.

    Will close the connection before exiting, and if there was an unhandled exception
    it will first perform a rollback and then close the connection.
    """
    engine = create_engine(config.database_url, echo=(config.debug == 1))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
