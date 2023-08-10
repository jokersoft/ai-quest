from sqlalchemy import Column, String, DateTime, Uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from uuid import uuid4

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4())
    name = Column(String(50))
    email = Column(String(50))
