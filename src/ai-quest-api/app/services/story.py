import logging
import uuid

from sqlalchemy.orm import Session

from app.entities.message import Message as MessageEntity
from app.entities.story import Story as StoryEntity
from app.repositories.story import StoryRepository
from app.repositories.message import MessageRepository
from app.schemas.story import Story as StorySchema
from app.schemas.message import Message as MessageSchema
from app.services.prompt_provider import PromptProvider

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class StoryService:
    def __init__(self, db: Session):
        self.db = db
        self._story_repository = StoryRepository(db)
        self._message_repository = MessageRepository(db)
        self._prompt_provider = PromptProvider()

    def init_story(self) -> tuple[StorySchema, list[MessageSchema]]:
        # Story
        story_entity = StoryEntity(user_id=uuid.uuid4().bytes)
        saved_story = self._story_repository.add(story_entity)
        _LOGGER.debug(f"Story.id: {saved_story.id}")
        _LOGGER.info(f"Story created with ID: {saved_story.id}")

        # Messages
        system_prompt = self._prompt_provider.get("system")
        messages_entities = [
            MessageEntity(role="system", content=system_prompt, story_id=saved_story.id),
            MessageEntity(role="user", content="Hello!", story_id=saved_story.id),
        ]
        for message in messages_entities:
            # TODO: timestamp or sequence number
            self._message_repository.add(message)

        # Convert entities to schema DTOs
        story_dto = StorySchema(
            id=str(uuid.UUID(bytes=saved_story.id)),
            user_id=str(uuid.UUID(bytes=saved_story.user_id))
        )
        messages_dtos = [
            MessageSchema(
                role=message.role,
                content=message.content
            ) for message in messages_entities
        ]

        return story_dto, messages_dtos
