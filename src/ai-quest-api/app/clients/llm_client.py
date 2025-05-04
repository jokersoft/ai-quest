from abc import ABC, abstractmethod
import os
import logging

import anthropic
from app.clients.config import config

_LOGGER = logging.getLogger(__name__)

class LLMClient(ABC):
    @abstractmethod
    def ask(self, question: str) -> dict:
        pass

    @abstractmethod
    def send_messages(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        pass


class AnthropicClient(LLMClient):
    """
    https://github.com/anthropics/anthropic-sdk-python
    https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts
    """
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=config.get("anthropic-api-key"),
            max_retries=0,
            timeout=20.0,  # seconds
        )
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.max_tokens = os.getenv("MAX_TOKENS", 1024)

    def ask(self, question: str) -> dict:
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
            )
        except anthropic.APIConnectionError as e:
            _LOGGER.exception("The server could not be reached", e.__cause__)
            raise e
        except anthropic.RateLimitError as e:
            _LOGGER.exception("The rate limit was exceeded", e.__cause__)
            raise e
        except anthropic.APIStatusError as e:
            _LOGGER.exception("The API returned an error", e.__cause__)
            raise e
        except Exception as e:
            _LOGGER.exception("An unexpected error occurred", e.__cause__)
            raise e

        return {"response": response.content}

    def send_messages(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        try:
            response = self.client.messages.create(
                max_tokens=self.max_tokens,
                messages=messages,
                tools=tools,
                response_format={"type": "json_object"},
                model=self.model,
            )
        except anthropic.APIConnectionError as e:
            _LOGGER.exception("The server could not be reached", e.__cause__)
        except anthropic.RateLimitError as e:
            _LOGGER.exception("The rate limit was exceeded", e.__cause__)
        except anthropic.APIStatusError as e:
            _LOGGER.exception("The API returned an error", e.__cause__)
        except Exception as e:
            _LOGGER.exception("An unexpected error occurred", e.__cause__)

        return {"response": response.content}


def create_client() -> LLMClient:
    client_type = os.getenv("LLM_CLIENT_TYPE", "anthropic")
    if client_type == "anthropic":
        return AnthropicClient()
    # Add more conditions here for other clients
    else:
        raise ValueError(f"Unsupported LLM client type: {client_type}")
