from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class ChapterMemory:
    """Represents a chapter memory - technology-agnostic"""
    story_id: uuid.UUID
    chapter_number: int
    chapter_data: dict[str, Any]  # Contains narration, situation, choices, action, outcome
    created_at: datetime


@dataclass
class MemorySearchResult:
    """Search result - technology-agnostic"""
    chapter_memory: ChapterMemory
    relevance_score: float


class MemoryStoreInterface(ABC):
    """Abstract interface for memory stores"""

    @abstractmethod
    async def add_memory(self, story_id: uuid.UUID,
                         chapter_number: int,
                         chapter_data: dict[str, Any]) -> None:
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