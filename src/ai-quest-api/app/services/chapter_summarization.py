import logging

from sqlalchemy.orm import Session

from app.clients import llm_client
from app.entities.chapter import Chapter
from app.repositories.chapter import ChapterRepository
from app.services.translator import Translator
from app.services.user import UserInfo

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class ChapterSummarizationService:
    def __init__(self, db: Session, user_info: UserInfo):
        self.translator = Translator.get_instance(user_info.locale)
        self.llm_client = llm_client.create_client(self.translator.translate("prompts.dm_summarize"), "anthropic")
        self.chapter_repository = ChapterRepository(db)
        self.user_info = user_info

    def _get_localized_prompt(self, chapter: Chapter) -> str:
        """Generate localized prompt based on user language."""
        return f"""{self.translator.translate('chapter_summarization.instruction')}

{self.translator.translate('chapter_summarization.narration_label')}: {chapter.narration}
{self.translator.translate('chapter_summarization.situation_label')}: {chapter.situation}
{self.translator.translate('chapter_summarization.action_label')}: {chapter.action}
{self.translator.translate('chapter_summarization.outcome_label')}: {chapter.outcome}

{self.translator.translate('chapter_summarization.summary_instruction')}"""

    def summarize_chapter(self, chapter: Chapter) -> str:
        """Summarize a chapter using the LLM client."""
        logger.debug("Starting chapter summarization")

        if chapter.summary is not None:
            return chapter.summary

        try:
            # Create a localized prompt with the chapter content
            prompt = self._get_localized_prompt(chapter)

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
