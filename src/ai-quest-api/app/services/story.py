import datetime
import logging
import uuid

from sqlalchemy.orm import Session

from app.entities.chapter import Chapter as ChapterEntity
from app.entities.message import Message as MessageEntity
from app.entities.story import Story as StoryEntity
from app.repositories.chapter import ChapterRepository
from app.repositories.story import StoryRepository
from app.repositories.message import MessageRepository
from app.services import dm
from app.services.user import UserInfo
from app.schemas.story import Story as StoryResponse, FullStory as FullStoryResponse

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

INITIAL_USER_MESSAGE = "Wake up!"  # Initial message to start the story

class StoryService:
    def __init__(self, db: Session):
        self.db = db
        self._dm = dm.DungeonMaster()
        self._story_repository = StoryRepository(db)
        self._message_repository = MessageRepository(db)
        self._chapter_repository = ChapterRepository(db)

    def get(self, story_id: uuid.UUID) -> FullStoryResponse:
        # Get story by ID
        story_entity = self._story_repository.get(story_id.bytes)
        if not story_entity:
            raise ValueError(f"Story with ID {story_id} not found")

        # Get the last chapter to extract current choices
        last_chapter = self._chapter_repository.get_last_chapter(story_id.bytes)
        current_choices = last_chapter.choices if last_chapter else []

        # Convert to response DTOs
        full_story = FullStoryResponse(
            id=story_entity.id,
            user_id=story_entity.user_id,
            title=story_entity.title,
            chapters=self._chapter_repository.get_chapters_by_story_id(story_id.bytes),
            current_choices=current_choices,
        )

        return full_story

    def init(self, user_info: UserInfo) -> FullStoryResponse:
        # Story init
        story_entity = StoryEntity(user_id=user_info.user_id.bytes)
        saved_story = self._story_repository.add(story_entity)
        story_id_uuid = uuid.UUID(bytes=saved_story.id)
        logger.debug(f"Story.id: {story_id_uuid}")
        logger.info(f"Story created with ID: {story_id_uuid}")

        # Get intro message from the LLM
        messages = [{"role": "user", "content": INITIAL_USER_MESSAGE}]
        dm_intro_message = self._dm.send_messages(messages)

        # Record the 1st chapter
        new_chapter = ChapterEntity(
            narration=dm_intro_message.narration,
            situation=dm_intro_message.situation,
            choices=dm_intro_message.choices,
            action=INITIAL_USER_MESSAGE,
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

        # Convert to response DTOs
        full_story = FullStoryResponse(
            id=saved_story.id,
            user_id=user_info.user_id,
            title=story_title,
            chapters=self._chapter_repository.get_chapters_by_story_id(saved_story.id),
            current_choices=dm_intro_message.choices,
        )

        return full_story

    def list(self, user_info: UserInfo) -> list[StoryResponse]:
        # Fetch stories for the user
        story_entities = self._story_repository.list_by_user_id(user_info.user_id.bytes)
        # Convert to schema DTOs
        stories = [
            StoryResponse(
                id=story.id,
                user_id=story.user_id,
                title=story.title
            )
            for story in story_entities
        ]
        return stories

    def act(self, story_id: uuid.UUID, user_decision: str) -> FullStoryResponse:
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

        # Convert to response DTOs
        full_story = FullStoryResponse(
            id=story_entity.id,
            user_id=story_entity.user_id,
            title=story_entity.title,
            chapters=self._chapter_repository.get_chapters_by_story_id(story_id.bytes),
            current_choices=assistant_response.choices,
        )

        return full_story

    def delete(self, story_id: uuid.UUID) -> None:
        self._story_repository.delete(story_id.bytes)
