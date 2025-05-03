from sqlalchemy import Column, BINARY
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Story(Base):
    __tablename__ = 'stories'

    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    user_id = Column(BINARY(16), nullable=False)
