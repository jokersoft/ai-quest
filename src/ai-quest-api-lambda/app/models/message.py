from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mysql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    role = Column(String(50))
    content = Column(String(1000))
    type = Column(String(50))
    timestamp = Column(DateTime(timezone=True), default=func.now())
