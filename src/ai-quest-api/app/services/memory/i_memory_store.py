from abc import ABC, abstractmethod
from dataclasses import dataclass
import uuid

from app.entities.chapter import Chapter as ChapterEntity
from app.schemas.story import Chapter


@dataclass
class MemorySearchResult:
    """Search result - technology-agnostic"""
    chapter: Chapter
    relevance_score: float


class MemoryStoreInterface(ABC):
    """Abstract interface for memory stores"""

    @abstractmethod
    async def add_memory(self, story_id: uuid.UUID, chapter: ChapterEntity) -> None:
        """Store a chapter as memory"""
        pass

    @abstractmethod
    async def search_memories(self, story_id: uuid.UUID,
                              query: str,
                              max_results: int = 5) -> list[MemorySearchResult]:
        """Search for relevant memories based on query"""
        pass

    @abstractmethod
    async def get_story_context(self, story_id: uuid.UUID,
                                current_situation: str,
                                max_chapters: int = 3) -> str:
        """Get formatted context for the story based on current situation"""
        pass

    @abstractmethod
    async def delete_story_memories(self, story_id: uuid.UUID) -> None:
        """Delete all memories for a story"""
        pass
