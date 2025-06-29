import datetime
import logging
import uuid
from random import choices

from sqlalchemy.orm import Session

from app.entities.chapter import Chapter as ChapterEntity
from app.entities.message import Message as MessageEntity
from app.entities.story import Story as StoryEntity
from app.repositories.chapter import ChapterRepository
from app.repositories.story import StoryRepository
from app.repositories.message import MessageRepository
from app.services import dm
from app.services.user import UserInfo
from app.schemas.story import Story as StorySchema, FullStory as FullStorySchema
from app.schemas.message import Message as MessageSchema

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class StoryService:
    def __init__(self, db: Session):
        self.db = db
        self._dm = dm.DungeonMaster()
        self._story_repository = StoryRepository(db)
        self._message_repository = MessageRepository(db)
        self._chapter_repository = ChapterRepository(db)

    def get(self, story_id: uuid.UUID) -> FullStorySchema:
        # Get story by ID
        story_entity = self._story_repository.get(story_id.bytes)
        if not story_entity:
            raise ValueError(f"Story with ID {story_id} not found")

        # Get messages for the story
        message_entities = self._message_repository.get_messages_by_story_id(story_id.bytes)

        # Convert Story to schema DTOs
        story_messages = [
            MessageSchema(
                role=message.role,
                content=message.content
            ) for message in message_entities
        ]

        full_story = FullStorySchema(
            id=str(uuid.UUID(bytes=story_entity.id)),
            user_id=str(uuid.UUID(bytes=story_entity.user_id)),
            messages=story_messages
        )

        return full_story

    def init(self, user_info: UserInfo) -> FullStorySchema:
        # Story init
        story_entity = StoryEntity(user_id=user_info.user_id.bytes)
        saved_story = self._story_repository.add(story_entity)
        story_id_uuid = uuid.UUID(bytes=saved_story.id)
        logger.debug(f"Story.id: {story_id_uuid}")
        logger.info(f"Story created with ID: {story_id_uuid}")

        # Get intro message from the LLM
        initial_user_message = "Hello!"
        messages = [{"role": "user", "content": initial_user_message}]
        dm_intro_message = self._dm.send_messages(messages)

        # Record the 1st chapter
        new_chapter = ChapterEntity(
            narration=dm_intro_message.narration,
            situation=dm_intro_message.situation,
            choices=dm_intro_message.choices,
            action=initial_user_message,
            outcome=dm_intro_message.outcome,
            number=1,
            story_id=saved_story.id
        )
        self._chapter_repository.add(new_chapter)

        # Save chat messages
        logger.debug(f"dm_intro_message.narration: {dm_intro_message.narration}")
        messages.append({"role": "assistant", "content": dm_intro_message.to_string()})

        # Update story title
        story_title = dm_intro_message.narration[:256]
        self._story_repository.update_title(saved_story.id, story_title)

        # Save new messages in the repository
        message_entities = []
        for message in messages:
            message_entity = MessageEntity(
                role=message.get("role"), content=message.get("content"), story_id=saved_story.id
            )
            self._message_repository.add(message_entity)
            message_entities.append(message_entity)

        # Convert Story to schema DTOs
        story_messages = [
            MessageSchema(
                role=message.role,
                content=message.content
            ) for message in message_entities
        ]

        # Create FullStory schema for response
        full_story = FullStorySchema(
            id=str(uuid.UUID(bytes=saved_story.id)),
            user_id=str(user_info.user_id),
            title=story_title,
            messages=story_messages,
            choices=dm_intro_message.choices,
        )

        return full_story

    def list(self, user_info: UserInfo) -> list[StorySchema]:
        # Fetch stories for the user
        story_entities = self._story_repository.list_by_user_id(user_info.user_id.bytes)
        # Convert to schema DTOs
        stories = [
            StorySchema(
                id=str(uuid.UUID(bytes=story.id)),
                user_id=str(uuid.UUID(bytes=story.user_id)),
                title=story.title
            )
            for story in story_entities
        ]
        return stories

    def act(self, story_id: uuid.UUID, user_decision: str) -> FullStorySchema:
        # Get existing story
        story_entity = self._story_repository.get(story_id.bytes)
        if not story_entity:
            raise ValueError(f"Story with ID {story_id} not found")

        # Get existing messages
        message_entities = self._message_repository.get_messages_by_story_id(story_id.bytes)

        # Add user message to the story
        user_message_entity = MessageEntity(
            role="user",
            content=user_decision,
            story_id=story_id.bytes,
            created_at=datetime.datetime.now(datetime.UTC),
        )
        message_entities.append(user_message_entity)

        # Format messages for LLM
        llm_messages = [
            {"role": message.role, "content": message.content}
            for message in message_entities
        ]

        # Get response from LLM
        assistant_response = self._dm.send_messages(llm_messages)

        # Record the 1st chapter
        new_chapter = ChapterEntity(
            narration=assistant_response.narration,
            situation=assistant_response.situation,
            choices=assistant_response.choices,
            action=user_decision,
            outcome=assistant_response.outcome,
            number=self._chapter_repository.get_max_chapter_number(story_id.bytes) + 1,
            story_id=story_id.bytes,
        )
        self._chapter_repository.add(new_chapter)

        # Save chat messages
        logger.debug(f"last_message narration: {assistant_response.narration}")
        llm_messages.append({"role": "assistant", "content": assistant_response})

        # Add LLM response to the story
        assistant_message_entity = MessageEntity(
            role="assistant",
            content=assistant_response.to_string(),
            story_id=story_id.bytes,
            created_at=datetime.datetime.now(datetime.UTC),
        )
        message_entities.append(assistant_message_entity)

        # Save when we have both messages
        self._message_repository.add(user_message_entity)
        self._message_repository.add(assistant_message_entity)

        # Convert to schema DTOs
        story_messages = [
            MessageSchema(
                role=message.role,
                content=message.content
            ) for message in message_entities
        ]

        full_story = FullStorySchema(
            id=str(uuid.UUID(bytes=story_entity.id)),
            user_id=str(uuid.UUID(bytes=story_entity.user_id)),
            messages=story_messages,
            choices=assistant_response.choices
        )

        return full_story
