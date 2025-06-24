from abc import ABC, abstractmethod
import logging

import anthropic
from app.clients import config
from app.services.prompt_provider import PromptProvider

_LOGGER = logging.getLogger(__name__)
config = config.Config()


class LLMClient(ABC):
    @abstractmethod
    def ask(self, question: str) -> dict:
        pass

    @abstractmethod
    def send_messages(self, messages: list[dict], tools: list[dict] | None = None) -> str:
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

        return response.content[0]

    def send_messages(self, messages: list[dict], tools: list[dict] | None = None) -> str:
        try:
            _LOGGER.warning(f"debug Anthropic: {messages}")
            response = self.client.messages.create(
                max_tokens=self.max_tokens,
                messages=messages,
                model=self.model,
                system=self.system_prompt,
            )
        except anthropic.APIConnectionError as e:
            _LOGGER.exception("The server could not be reached", exc_info=True)
            raise e
        except anthropic.RateLimitError as e:
            _LOGGER.exception("The rate limit was exceeded", exc_info=True)
            raise e
        except anthropic.APIStatusError as e:
            _LOGGER.exception("The API returned an error", exc_info=True)
            raise e
        except Exception as e:
            _LOGGER.exception("An unexpected error occurred", exc_info=True)
            raise e

        return response.content[0].text


def create_client() -> LLMClient:
    if config.llm_client_type == "anthropic":
        return AnthropicClient()
    # Add more conditions here for other clients
    else:
        raise ValueError(f"Unsupported LLM client type: {config.llm_client_type}")
