import datetime
import logging
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app.entities.chapter import Chapter as ChapterEntity
from app.entities.message import Message as MessageEntity
from app.entities.story import Story as StoryEntity
from app.repositories.chapter import ChapterRepository
from app.repositories.story import StoryRepository
from app.repositories.message import MessageRepository
from app.services import dm
from app.services.memory.i_memory_store import MemoryStoreInterface
from app.services.translator import Translator
from app.services.story_context import StoryContext
from app.services.user import UserInfo
from app.schemas.story import Story as StoryResponse, FullStory as FullStoryResponse

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class StoryService:
    def __init__(self, db: Session, user_info: UserInfo, memory_service: Optional[MemoryStoreInterface] = None):
        self.db = db
        self.user_info = user_info
        self.dm = dm.DungeonMaster(user_info)
        self.story_repository = StoryRepository(db)
        self.message_repository = MessageRepository(db)
        self.chapter_repository = ChapterRepository(db)
        self.memory_service = memory_service
        self.story_context_service = StoryContext(db, user_info, memory_service)
        self.translator = Translator.get_instance(user_info.locale)

    def get(self, story_id: uuid.UUID) -> FullStoryResponse:
        # Get story by ID
        story_entity = self.story_repository.get(story_id.bytes)
        if not story_entity:
            raise ValueError(f"Story with ID {story_id} not found")

        # Get the last chapter to extract current choices
        last_chapter = self.chapter_repository.get_last_chapter(story_id.bytes)
        current_choices = last_chapter.choices_list if last_chapter else []

        # Get chapters and convert them to proper format
        chapter_entities = self.chapter_repository.get_chapters_by_story_id(story_id.bytes)

        # Convert to response DTOs
        full_story = FullStoryResponse(
            id=story_entity.id,
            user_id=story_entity.user_id,
            title=story_entity.title,
            chapters=chapter_entities,
            current_choices=current_choices,
        )

        return full_story

    async def init(self, user_info: UserInfo) -> FullStoryResponse:
        # Story init
        story_entity = StoryEntity(user_id=user_info.user_id.bytes)
        saved_story = self.story_repository.add(story_entity)
        story_id_uuid = uuid.UUID(bytes=saved_story.id)
        logger.debug(f"Story.id: {story_id_uuid}")
        logger.info(f"Story created with ID: {story_id_uuid}")

        # Get intro message from the LLM
        initial_user_message = self.translator.translate('prompts.1st_user_message')

        messages = [{"role": "user", "content": initial_user_message}]
        dm_intro_message = self.dm.send_messages(messages)

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
        self.chapter_repository.add(new_chapter)

        # Store in memory service if available
        if self.memory_service:
            try:
                await self.memory_service.add_memory(
                    story_id=story_id_uuid,
                    chapter=new_chapter
                )
            except Exception as e:
                logger.warning(f"Failed to store memory: {e}")

        # Save chat messages
        logger.debug(f"dm_intro_message.narration: {dm_intro_message.narration}")
        messages.append({"role": "assistant", "content": dm_intro_message.to_string()})

        # Update story title
        story_title = dm_intro_message.narration[:256]
        self.story_repository.update_title(saved_story.id, story_title)

        # Save new messages in the repository
        message_entities = []
        for message in messages:
            message_entity = MessageEntity(
                role=message.get("role"), content=message.get("content"), story_id=saved_story.id
            )
            self.message_repository.add(message_entity)
            message_entities.append(message_entity)

        # Get chapters and convert them to proper format
        chapter_entities = self.chapter_repository.get_chapters_by_story_id(saved_story.id)

        # Convert to response DTOs
        full_story = FullStoryResponse(
            id=saved_story.id,
            user_id=user_info.user_id,
            title=story_title,
            chapters=chapter_entities,
            current_choices=dm_intro_message.choices,
        )

        return full_story

    def list(self, user_info: UserInfo) -> list[StoryResponse]:
        # Fetch stories for the user
        story_entities = self.story_repository.list_by_user_id(user_info.user_id.bytes)
        # Convert to schema DTOs
        stories = [
            StoryResponse(
                id=story.id,
                user_id=story.user_id,
                title=story.title,
                is_over=story.is_over,
            )
            for story in story_entities
        ]
        return stories

    async def act(self, story_id: uuid.UUID, user_decision: str) -> FullStoryResponse:
        # Get existing story
        story_entity = self.story_repository.get(story_id.bytes)
        if not story_entity:
            raise ValueError(f"Story with ID {story_id} not found")

        if story_entity.is_over:
            raise ValueError(f"Story with ID {story_id} is already over")

        # Get existing messages
        message_entities = self.message_repository.get_messages_by_story_id(story_id.bytes)

        # Get memory context if memory service is available
        memory_context = ""
        if self.memory_service:
            try:
                # Get last chapter for current situation
                last_chapter = self.chapter_repository.get_last_chapter(story_id.bytes)
                current_situation = last_chapter.situation if last_chapter else user_decision

                # Get relevant memories
                memory_context = await self.story_context_service.provide_context(story_id, current_situation)
            except Exception as e:
                logger.warning(f"Failed to get memory context: {e}")

        user_decision_with_context = f"Relevant past events for context:\n{memory_context}\n\nCurrent action: {user_decision}" if memory_context else user_decision

        # Add user message to the story
        user_message_entity = MessageEntity(
            role="user",
            content=user_decision_with_context,
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
        assistant_response = self.dm.send_messages(llm_messages)

        # If Death
        if assistant_response.is_death:
            self.story_repository.end_story(story_id.bytes)

        # Record the new chapter
        new_chapter_number = self.chapter_repository.get_max_chapter_number(story_id.bytes) + 1
        new_chapter = ChapterEntity(
            narration=assistant_response.narration,
            situation=assistant_response.situation,
            choices=assistant_response.choices,
            action=user_decision,
            outcome=assistant_response.outcome,
            number=new_chapter_number,
            story_id=story_id.bytes,
        )
        self.chapter_repository.add(new_chapter)

        # Store in memory service if available
        if self.memory_service:
            try:
                await self.memory_service.add_memory(
                    story_id,
                    chapter=new_chapter,
                )
            except Exception as e:
                logger.warning(f"Failed to store memory: {e}")

        # Save chat messages
        logger.debug(f"last_message narration: {assistant_response.narration}")
        llm_messages.append({"role": "assistant", "content": assistant_response.to_string()})

        # Add LLM response to the story
        assistant_message_entity = MessageEntity(
            role="assistant",
            content=assistant_response.to_string(),
            story_id=story_id.bytes,
            created_at=datetime.datetime.now(datetime.UTC),
        )
        message_entities.append(assistant_message_entity)

        # Save when we have both messages
        self.message_repository.add(user_message_entity)
        self.message_repository.add(assistant_message_entity)

        # Convert to response DTOs with proper UUID conversion
        chapter_entities = self.chapter_repository.get_chapters_by_story_id(story_id.bytes)

        # Convert to response DTOs
        full_story = FullStoryResponse(
            id=story_entity.id,
            user_id=story_entity.user_id,
            title=story_entity.title,
            chapters=chapter_entities,
            current_choices=assistant_response.choices,
            is_over=assistant_response.is_death,
        )

        return full_story

    async def delete(self, story_id: uuid.UUID) -> None:
        """Delete story and associated memories"""
        self.story_repository.delete(story_id.bytes)

        # Clean up memories if service is available
        if self.memory_service:
            try:
                await self.memory_service.delete_story_memories(story_id)
            except Exception as e:
                logger.warning(f"Failed to delete story memories: {e}")
