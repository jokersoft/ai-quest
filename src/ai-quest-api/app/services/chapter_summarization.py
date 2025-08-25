import json
import logging
import os

from sqlalchemy.orm import Session

from app.clients import llm_client
from app.entities.chapter import Chapter
from app.repositories.chapter import ChapterRepository
from app.services.prompt_provider import PromptProvider
from app.services.user import UserInfo

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class ChapterSummarizationService:
    def __init__(self, db: Session, user_info: UserInfo):
        self.llm_client = llm_client.create_client(PromptProvider().get("dm_summarize"), "anthropic")
        self.chapter_repository = ChapterRepository(db)
        self.user_info = user_info
        self._load_translations()

    def _load_translations(self):
        """Load translations from JSON file."""
        translations_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'translations',
            'chapter_summarization.json'
        )
        with open(translations_path, 'r', encoding='utf-8') as f:
            self.translations = json.load(f)

    def _get_localized_prompt(self, chapter: Chapter) -> str:
        """Generate localized prompt based on user language."""
        language = getattr(self.user_info, 'language', 'en')
        if language not in self.translations:
            language = 'en'

        t = self.translations[language]

        return f"""{t['instruction']}

{t['narration_label']}: {chapter.narration}
{t['situation_label']}: {chapter.situation}
{t['action_label']}: {chapter.action}
{t['outcome_label']}: {chapter.outcome}

{t['summary_instruction']}"""

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
