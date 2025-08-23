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
    summary = Column(Text, nullable=True)
    number = Column(Integer, nullable=False)
    story_id = Column(BINARY(16), nullable=False, index=True)

    @property
    def id_uuid(self) -> uuid.UUID:
        """Convert binary ID to UUID object"""
        return uuid.UUID(bytes=self.id) if self.id else None

    @property
    def story_id_uuid(self) -> uuid.UUID:
        """Convert binary story_id to UUID object"""
        return uuid.UUID(bytes=self.story_id) if self.story_id else None

    @property
    def choices_list(self) -> list[str]:
        """Convert choices to proper list format"""
        if isinstance(self.choices, str):
            try:
                return json.loads(self.choices)
            except (json.JSONDecodeError, TypeError):
                return []
        elif isinstance(self.choices, list):
            return self.choices
        else:
            return []

    def to_dict(self):
        """Make the entity directly serializable"""
        return {
            'id': str(self.id_uuid) if self.id else None,
            'narration': self.narration,
            'situation': self.situation,
            'choices': self.choices_list,
            'action': self.action,
            'outcome': self.outcome,
            'summary': self.summary,
            'number': self.number,
            'story_id': str(self.story_id_uuid) if self.story_id else None
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
