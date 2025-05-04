import logging

from sqlalchemy.orm import Session
from uuid import uuid4

from app.entities.message import Message
from app.entities.story import Story
from app.repositories.story import StoryRepository
from app.repositories.message import MessageRepository
from app.services.prompt_provider import PromptProvider

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class StoryService:
    def __init__(self, db: Session):
        self.db = db
        self._story_repository = StoryRepository(db)
        self._message_repository = MessageRepository(db)
        self._prompt_provider = PromptProvider()

    def init_story(self) -> tuple[Story, list[Message]]:
        # Story
        story = Story(user_id=uuid4().bytes)
        saved_story = self._story_repository.add(story)
        _LOGGER.debug(f"Story.id: {story.id}")
        _LOGGER.info(f"Story created with ID: {saved_story.id}")

        # Messages
        system_prompt = self._prompt_provider.get("system")
        messages = [
            Message(role="system", content=system_prompt, story_id=saved_story.id),
            Message(role="user", content="Hello!", story_id=saved_story.id),
        ]
        for message in messages:
            # TODO: timestamp or sequence number
            self._message_repository.add(message)

        return saved_story, messages
