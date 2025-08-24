from abc import ABC, abstractmethod
import json
import logging
from typing import Literal

import anthropic
import boto3

from app.clients import config
from app.clients.token_tracker import DynamoDBTokenTracker

logger = logging.getLogger(__name__)
config = config.Config()


class LLMClient(ABC):
    def __init__(self):
        self.token_tracker = DynamoDBTokenTracker()

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
    def __init__(self, system_prompt: str):
        super().__init__()
        self.client = anthropic.Anthropic(
            api_key=config.anthropic_api_key,
            max_retries=0,
            timeout=60.0,  # seconds
        )
        self.model = config.anthropic_model
        self.max_tokens = config.anthropic_max_tokens
        self.system_prompt = system_prompt

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

            # Track token usage
            if hasattr(response, 'usage'):
                self.token_tracker.track_usage(
                    service="anthropic",
                    model=self.model,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    metadata={
                        "method": "ask",
                        "question_length": len(question),
                        "system_prompt_length": len(self.system_prompt)
                    }
                )

            return response.content[0].text

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

            # Track token usage
            if hasattr(response, 'usage'):
                self.token_tracker.track_usage(
                    service="anthropic",
                    model=self.model,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    metadata={
                        "method": "send_messages",
                        "message_count": len(messages),
                        "has_tools": tools != anthropic.NotGiven(),
                        "system_prompt_length": len(self.system_prompt)
                    }
                )

            # Extract the tool use response
            for content in response.content:
                if content.type == "tool_use":
                    return json.dumps(content.input)

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
            logger.exception("Error in Anthropic API call", exc_info=True)
            raise e


class BedrockClaudeClient(LLMClient):
    """AWS Bedrock client for Claude models with token tracking"""

    def __init__(self, system_prompt: str, model_id: str = None):
        super().__init__()
        self.bedrock_client = boto3.client('bedrock-runtime')
        self.model_id = model_id or 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        self.system_prompt = system_prompt
        self.max_tokens = config.anthropic_max_tokens

    def ask(self, question: str) -> str:
        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": self.system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            }

            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            result = json.loads(response['body'].read())

            # Track token usage
            if 'usage' in result:
                self.token_tracker.track_usage(
                    service="bedrock",
                    model=self.model_id,
                    input_tokens=result['usage'].get('input_tokens', 0),
                    output_tokens=result['usage'].get('output_tokens', 0),
                    metadata={
                        "method": "ask",
                        "question_length": len(question),
                        "system_prompt_length": len(self.system_prompt)
                    }
                )

            return result['content'][0]['text']

        except Exception as e:
            logger.exception("Error in Bedrock API call", exc_info=True)
            raise e

    def send_messages(self, messages: list[dict], tools: list[dict] = None,
                      tool_choice: dict = None) -> str:
        """Send messages to Bedrock Claude with optional tool use"""
        try:
            # Build request body for Bedrock Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": self.system_prompt,
                "messages": messages
            }

            # Add tools if provided
            if tools:
                request_body["tools"] = tools

            # Add tool choice if provided
            if tool_choice:
                request_body["tool_choice"] = tool_choice

            # Make the Bedrock API call
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            # Parse the response
            result = json.loads(response['body'].read())

            # Track token usage
            if 'usage' in result:
                self.token_tracker.track_usage(
                    service="bedrock",
                    model=self.model_id,
                    input_tokens=result['usage'].get('input_tokens', 0),
                    output_tokens=result['usage'].get('output_tokens', 0),
                    metadata={
                        "method": "send_messages",
                        "message_count": len(messages),
                        "has_tools": tools is not None,
                        "has_tool_choice": tool_choice is not None,
                        "system_prompt_length": len(self.system_prompt)
                    }
                )

            # Extract tool use response if present
            if 'content' in result:
                for content_block in result['content']:
                    if isinstance(content_block, dict) and content_block.get('type') == 'tool_use':
                        # Return the tool input as JSON string
                        return json.dumps(content_block.get('input', {}))

                # If no tool use, return the text content
                for content_block in result['content']:
                    if isinstance(content_block, dict) and content_block.get('type') == 'text':
                        return content_block.get('text', '')

            # Fallback to returning the entire content if structure is different
            return json.dumps(result.get('content', ''))

        except Exception as e:
            logger.exception("Error in Bedrock API call", exc_info=True)
            raise e


def create_client(system_prompt: str, llm_family: str = Literal["anthropic", "bedrock"]) -> LLMClient:
    """Factory function to create appropriate LLM client

    Args:
        system_prompt: System prompt for the model
        llm_family: "anthropic" or "bedrock"
    """
    if llm_family == "anthropic":
        return AnthropicClient(system_prompt)
    elif llm_family == "bedrock":
        return BedrockClaudeClient(system_prompt)
    else:
        raise ValueError(f"Unsupported LLM client type: {config.llm_client_type}")
