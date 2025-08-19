import json
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

    def to_dict(self) -> dict:
        return {
            'id': uuid.UUID(bytes=self.id).hex if self.id else None,
            'narration': self.narration,
            'situation': self.situation,
            'choices': self.choices,
            'action': self.action,
            'outcome': self.outcome,
            'number': self.number,
            'story_id': uuid.UUID(bytes=self.story_id).hex if self.story_id else None
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
