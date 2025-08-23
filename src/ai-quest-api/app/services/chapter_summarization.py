import logging

from sqlalchemy.orm import Session

from app.clients import llm_client
from app.entities.chapter import Chapter
from app.repositories.chapter import ChapterRepository

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class ChapterSummarizationService:
    def __init__(self, db: Session):
        self.llm_client = llm_client.create_client()
        self.chapter_repository = ChapterRepository(db)

    def summarize_chapter(self, chapter: Chapter) -> str:
        """Summarize a chapter using the LLM client."""
        logger.debug("Starting chapter summarization")

        if chapter.summary is not None:
            return chapter.summary

        try:
            # Create a prompt with the chapter content
            prompt = f"""Please provide a concise summary of this chapter of the book:

Narration: {chapter.narration}
Situation: {chapter.situation}
Action: {chapter.action}
Outcome: {chapter.outcome}

Create a brief summary that captures the key events and developments in this chapter."""

            # Use the LLM client to generate the summary
            response = self.llm_client.ask(prompt)

            # Extract text from the response
            summary = response.text if hasattr(response, 'text') else str(response)

            logger.debug(f"Chapter summary: {summary}")
            chapter.summary = summary
            # Save the summary back to the chapter entity
            self.chapter_repository.update(chapter)

            return summary

        except Exception as e:
            logger.error(f"Failed to summarize chapter: {str(e)}")
            raise e
