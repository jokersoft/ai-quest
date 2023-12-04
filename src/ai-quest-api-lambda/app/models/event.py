from sqlalchemy import Column, String, Integer, DateTime, Uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from uuid import uuid4

Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4())
    subject = Column(String(100))
    delta = Column(Integer())
    reason = Column(String(1000))
    impact = Column(String(1000))
    timestamp = Column(DateTime(timezone=True), default=func.now())
