from sqlalchemy import Column, String, DateTime, Uuid
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4())
    user_id = Column(Uuid(as_uuid=True), index=True)
    role = Column(String(50))
    content = Column(String(1000))
    type = Column(String(50))
    timestamp = Column(DateTime(timezone=True), default=func.now())
