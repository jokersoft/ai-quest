from abc import ABC, abstractmethod
import json
import logging

import anthropic
from app.clients import config
from app.services.prompt_provider import PromptProvider

logger = logging.getLogger(__name__)
config = config.Config()


class LLMClient(ABC):
    @abstractmethod
    def ask(self, question: str) -> dict:
        pass

    @abstractmethod
    def send_messages(self, messages: list[dict], tools: list[dict] = None, tool_choice: dict = None) -> str:
        pass


class AnthropicClient(LLMClient):
    """
    https://github.com/anthropics/anthropic-sdk-python
    https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts
    """
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=config.anthropic_api_key,
            max_retries=0,
            timeout=60.0,  # seconds
        )
        self.model = config.anthropic_model
        self.max_tokens = config.anthropic_max_tokens
        self.system_prompt = PromptProvider().get("system")
        # Define the tool for structured responses
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


    def ask(self, question: str) -> str:
        try:
            response = self.client.messages.create(
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                model=self.model,
                system=self.system_prompt,
            )
        except anthropic.APIConnectionError as e:
            logger.exception("The server could not be reached", e.__cause__)
            raise e
        except anthropic.RateLimitError as e:
            logger.exception("The rate limit was exceeded", e.__cause__)
            raise e
        except anthropic.APIStatusError as e:
            logger.exception("The API returned an error", e.__cause__)
            raise e
        except Exception as e:
            logger.exception("An unexpected error occurred", e.__cause__)
            raise e

        return response.content[0]

    def send_messages(self, messages: list[dict], tools: list[dict] = None, tool_choice: dict = None) -> str:
        try:
            if tools is None:
                tools = anthropic.NotGiven()
            if tool_choice is None:
                tool_choice = anthropic.NotGiven()

            # https://docs.anthropic.com/en/api/client-sdks
            response = self.client.messages.create(
                max_tokens=self.max_tokens,
                messages=messages,
                model=self.model,
                system=self.system_prompt,
                tools=tools,
                tool_choice=tool_choice
            )

            # Extract the tool use response
            for content in response.content:
                if content.type == "tool_use":
                    return json.dumps(content.input)

            # Fallback if no tool use (shouldn't happen with tool_choice)
            return response.content[0].text

        except anthropic.APIConnectionError as e:
            logger.exception("The server could not be reached", exc_info=True)
            raise e
        except anthropic.RateLimitError as e:
            logger.exception("The rate limit was exceeded", exc_info=True)
            raise e
        except anthropic.APIStatusError as e:
            logger.exception("The API returned an error", exc_info=True)
            raise e
        except Exception as e:
            logger.exception("An unexpected error occurred", exc_info=True)
            raise e


def create_client() -> LLMClient:
    if config.llm_client_type == "anthropic":
        return AnthropicClient()
    # Add more conditions here for other clients
    else:
        raise ValueError(f"Unsupported LLM client type: {config.llm_client_type}")
