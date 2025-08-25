import json
import logging

from app.clients import llm_client
from app.services.translator import Translator
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
        self.translator = Translator.get_instance(user_info.locale)
        self.llm_client = llm_client.create_client(self.translator.translate("prompts.dungeon_master"), "anthropic")
        self.story_response_tool = self._create_localized_tool()
        self.tool_choice = {"type": "tool", "name": "story_response"}

    def _create_localized_tool(self) -> dict:
        """Create localized story_response_tool."""
        return {
            "name": self.translator.translate("dungeon_master.tool_name"),
            "description": self.translator.translate("dungeon_master.tool_description"),
            "input_schema": {
                "type": "object",
                "properties": {
                    "narration": {
                        "type": "string",
                        "description": self.translator.translate("dungeon_master.narration_description")
                    },
                    "outcome": {
                        "type": "string",
                        "description": self.translator.translate("dungeon_master.outcome_description")
                    },
                    "situation": {
                        "type": "string",
                        "description": self.translator.translate("dungeon_master.situation_description")
                    },
                    "choices": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": self.translator.translate("dungeon_master.choices_description"),
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
