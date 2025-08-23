from abc import ABC, abstractmethod
from dataclasses import dataclass
import uuid

from app.entities.chapter import Chapter as ChapterEntity


@dataclass
class MemorySearchResult:
    """Search result - technology-agnostic"""
    chapter_number: int
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
    async def delete_story_memories(self, story_id: uuid.UUID) -> None:
        """Delete all memories for a story"""
        pass
