import json
import logging

from app.clients import llm_client

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
    def __init__(self):
        self.llm_client = llm_client.create_client()
        self.story_response_tool = {
            "name": "story_response",
            "description": "Respond with the story outcome and next situation",
            "input_schema": {
                "type": "object",
                "properties": {
                    "narration": {
                        "type": "string",
                        "description": "A dry, sardonic comment or flavor text"
                    },
                    "outcome": {
                        "type": "string",
                        "description": "Description of what happened as a result of the player's action"
                    },
                    "situation": {
                        "type": "string",
                        "description": "The current situation the player faces"
                    },
                    "choices": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of choices available to the player",
                        "minItems": 3,
                        "maxItems": 6
                    }
                },
                "required": ["narration", "outcome", "situation", "choices"]
            }
        }
        self.tool_choice = {"type": "tool", "name": "story_response"}

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
