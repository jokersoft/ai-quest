from sqlalchemy import Column, String, Uuid
from sqlalchemy.orm import declarative_base
from uuid import uuid4

Base = declarative_base()


class Action(Base):
    __tablename__ = 'actions'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    message_id = Column(String(50), index=True)
    text = Column(String(256))
