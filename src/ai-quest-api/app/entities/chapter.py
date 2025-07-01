import uuid

from sqlalchemy import Column, BINARY, JSON, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    narration = Column(Text, nullable=False)
    situation = Column(Text, nullable=False)
    choices = Column(JSON, nullable=False)
    action = Column(Text, nullable=False)
    outcome = Column(Text, nullable=False)
    number = Column(Integer, nullable=False)
    story_id = Column(BINARY(16), nullable=False, index=True)
