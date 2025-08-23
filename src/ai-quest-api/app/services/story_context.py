import logging
import uuid

from sqlalchemy.orm import Session

from app.repositories.chapter import ChapterRepository
from app.repositories.story import StoryRepository
from app.services.chapter_summarization import ChapterSummarizationService
from app.services.memory.i_memory_store import MemoryStoreInterface

CONTEXT_CHAPTERS_NUM = 3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class StoryContext:
    def __init__(self, db: Session, memory_store: MemoryStoreInterface):
        self.story_repository = StoryRepository(db)
        self.chapter_repository = ChapterRepository(db)
        self.memory_store = memory_store
        self.chapter_summarization_service = ChapterSummarizationService(db)

    async def provide_context_async(self, story_id: uuid.UUID, user_decision: str) -> str:
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
            return "No previous context available."

        logger.debug(f"memory search_results count: {len(search_results)}")

        # Format context for the DM
        context_parts = ["Previous relevant events in this story:"]

        # Sort by chapter number to maintain chronological order
        for result in sorted(search_results, key=lambda x: x.chapter_memory.chapter_number):
            chapter = self.chapter_repository.get_chapter(story_id.bytes, result.chapter_number)
            chapter_summary = self.chapter_summarization_service.summarize_chapter(chapter)
            context_parts.append(
                f"\n[Chapter {chapter.number}] (relevance: {result.relevance_score:.2f}): {chapter_summary}"
            )
            logger.debug(f"chapter {chapter.number} relevance: {result.relevance_score}")
            logger.debug(f"chapter {chapter.number} summary: {chapter_summary}")

        return "\n".join(context_parts)
