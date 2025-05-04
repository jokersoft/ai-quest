import logging
import uuid

from app.entities.story import Story

_LOGGER = logging.getLogger(__name__)


class StoryRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def add(self, story: Story) -> Story:
        self.db_session.add(story)
        _LOGGER.info(f"Inserted a new story: {story.id}")

        self.db_session.commit()
        self.db_session.refresh(story)
        return story

    def get(self, story_id: uuid.UUID) -> Story:
        return self.db_session.query(Story).filter(Story.id == story_id).first()
