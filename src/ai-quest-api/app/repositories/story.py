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

    def get(self, story_id_bytes: bytes) -> Story | None:
        return self.db_session.query(Story).filter(Story.id == story_id_bytes).first()

    def update_title(self, story_id_bytes: bytes, title: str) -> Story:
        story_id_str = str(uuid.UUID(bytes=story_id_bytes))

        existing_story = self.get(story_id_bytes)
        if not existing_story:
            raise ValueError(f"Story with ID {story_id_str} not found")

        existing_story.title = title

        self.db_session.commit()
        self.db_session.refresh(existing_story)

        _LOGGER.info(f"Updated story title for: {story_id_str}")

        return existing_story

    def list_by_user_id(self, user_id_bytes: bytes) -> list[Story]:
        return (
            self.db_session.query(Story)
            .filter(Story.user_id == user_id_bytes)
            .all()
        )

    def delete(self, story_id_bytes: bytes) -> None:
        story_id_str = str(uuid.UUID(bytes=story_id_bytes))

        existing_story = self.get(story_id_bytes)
        if not existing_story:
            raise ValueError(f"Story with ID {story_id_str} not found")

        self.db_session.delete(existing_story)
        self.db_session.commit()

        _LOGGER.info(f"Deleted story: {story_id_str}")
