import json
import logging
import os

from app.clients import llm_client
from app.services.prompt_provider import PromptProvider
from app.services.user import UserInfo

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class DMResponse:
    def __init__(self, narration: str, outcome: str, situation: str, choices: list[str]):
        self.narration = narration
        self.outcome = outcome
        self.situation = situation
        self.choices = choices

    def to_dict(self):
        return {
            "narration": self.narration,
            "outcome": self.outcome,
            "situation": self.situation,
            "choices": self.choices
        }

    def to_string(self):
        return json.dumps(self.to_dict())


class DungeonMaster:
    def __init__(self, user_info: UserInfo):
        self.user_info = user_info
        self.llm_client = llm_client.create_client(PromptProvider(user_info.locale).get("dungeon_master"), "anthropic")
        self._load_translations()
        self.story_response_tool = self._create_localized_tool()
        self.tool_choice = {"type": "tool", "name": "story_response"}

    def _load_translations(self):
        """Load translations from JSON file."""
        translations_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'translations',
            'dungeon_master.json'
        )
        with open(translations_path, 'r', encoding='utf-8') as f:
            self.translations = json.load(f)

    def _get_localized_text(self, key: str) -> str:
        """Get localized text based on user language."""
        language = getattr(self.user_info, 'language', 'en')
        if language not in self.translations:
            language = 'en'
        return self.translations[language].get(key, self.translations['en'][key])

    def _create_localized_tool(self) -> dict:
        """Create localized story_response_tool."""
        return {
            "name": self._get_localized_text("tool_name"),
            "description": self._get_localized_text("tool_description"),
            "input_schema": {
                "type": "object",
                "properties": {
                    "narration": {
                        "type": "string",
                        "description": self._get_localized_text("narration_description")
                    },
                    "outcome": {
                        "type": "string",
                        "description": self._get_localized_text("outcome_description")
                    },
                    "situation": {
                        "type": "string",
                        "description": self._get_localized_text("situation_description")
                    },
                    "choices": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": self._get_localized_text("choices_description"),
                        "minItems": 3,
                        "maxItems": 6
                    }
                },
                "required": ["narration", "outcome", "situation", "choices"]
            }
        }

    def send_messages(self, messages: list[dict]) -> DMResponse:
        try:
            response_str = self.llm_client.send_messages(messages, tools=[self.story_response_tool], tool_choice=self.tool_choice)
            response_dict = json.loads(response_str)

            return DMResponse(
                narration=response_dict["narration"],
                outcome=response_dict["outcome"],
                situation=response_dict["situation"],
                choices=response_dict["choices"]
            )
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON DMResponse", exc_info=True)
            raise ValueError("Invalid JSON DMResponse") from e
        except KeyError as e:
            logger.error(f"Missing expected key in DMResponse: {e}", exc_info=True)
            raise ValueError(f"Missing key in DMResponse: {e}") from e
        except Exception as e:
            logger.exception("An unexpected error happened to DM", exc_info=True)
            raise e
