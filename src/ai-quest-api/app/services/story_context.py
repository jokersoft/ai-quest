import json
import logging
import os
import uuid

from sqlalchemy.orm import Session

from app.repositories.chapter import ChapterRepository
from app.repositories.story import StoryRepository
from app.services.chapter_summarization import ChapterSummarizationService
from app.services.memory.i_memory_store import MemoryStoreInterface
from app.services.user import UserInfo

CONTEXT_CHAPTERS_NUM = 3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class StoryContext:
    def __init__(self, db: Session, user_info: UserInfo, memory_store: MemoryStoreInterface):
        self.user_info = user_info
        self.story_repository = StoryRepository(db)
        self.chapter_repository = ChapterRepository(db)
        self.memory_store = memory_store
        self.chapter_summarization_service = ChapterSummarizationService(db, user_info)
        self._load_translations()

    def _load_translations(self):
        """Load translations from JSON file."""
        translations_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'translations',
            'story_context.json'
        )
        with open(translations_path, 'r', encoding='utf-8') as f:
            self.translations = json.load(f)

    def _get_localized_text(self, key: str) -> str:
        """Get localized text based on user language."""
        language = getattr(self.user_info, 'language', 'en')
        if language not in self.translations:
            language = 'en'
        return self.translations[language].get(key, self.translations['en'][key])

    async def provide_context(self, story_id: uuid.UUID, user_decision: str) -> str:
        """Async version that can safely call memory store without blocking main thread"""
        last_chapter = self.chapter_repository.get_last_chapter(story_id.bytes)
        current_situation = f"""{last_chapter.situation}
{user_decision}"""

        if not last_chapter:
            raise ValueError(f"Last chapter for story {story_id} not found")

        # Search for relevant N chapters
        search_results = await self.memory_store.search_memories(
            story_id=story_id,
            query=current_situation,
            max_results=CONTEXT_CHAPTERS_NUM,
        )

        if not search_results:
            return self._get_localized_text("no_context")

        logger.debug(f"memory search_results count: {len(search_results)}")

        # Format context for the DM
        context_parts = [self._get_localized_text("previous_events")]

        # Sort by chapter number to maintain chronological order
        for result in sorted(search_results, key=lambda search_result: search_result.chapter_number):
            chapter = self.chapter_repository.get_chapter(story_id.bytes, result.chapter_number)
            chapter_summary = self.chapter_summarization_service.summarize_chapter(chapter)
            context_parts.append(
                f"\n[{self._get_localized_text('chapter_label')} {chapter.number}] ({self._get_localized_text('relevance_label')}: {result.relevance_score:.2f}): {chapter_summary}"
            )
            logger.debug(f"chapter {chapter.number} relevance: {result.relevance_score}")
            logger.debug(f"chapter {chapter.number} summary: {chapter_summary}")

        return "\n".join(context_parts)
