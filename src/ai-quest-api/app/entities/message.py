import datetime
import uuid

from sqlalchemy import Column, BINARY, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    story_id = Column(BINARY(16), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
