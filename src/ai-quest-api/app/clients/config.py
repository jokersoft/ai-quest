import boto3
import json
import logging
import os
from botocore.config import Config as BotoConfig


_LOGGER = logging.getLogger(__name__)


def get_secret(secret_name) -> dict:
    _LOGGER.info("aaa")
    # Create a Config object with timeout settings
    boto_config = BotoConfig(
        connect_timeout=5,  # Connection timeout in seconds
        read_timeout=10  # Read timeout in seconds
    )

    _LOGGER.info("bbb")
    # Pass the config object to the boto3 client
    client = boto3.client('secretsmanager', config=boto_config)

    try:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager/client/get_secret_value.html
        response = client.get_secret_value(SecretId=secret_name)
        _LOGGER.info("response")
        secret = response.get('SecretString')
        return json.loads(secret)
    except Exception as e:
        _LOGGER.exception(f"Error retrieving secret {secret_name}: {e}")
        raise e


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # CONFIG_NAME = os.environ.get("CONFIG_NAME")
        # if CONFIG_NAME is None:
        #     raise ValueError("CONFIG_NAME environment variable is not set.")
        # secrets = get_secret(CONFIG_NAME)

        # secrets
        self.api_key: str = os.environ.get("API_KEY")
        self.database_url: str = os.environ.get("DATABASE_URL")
        self.anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY")

        # configs
        self.app_version: str = os.environ.get("APP_VERSION")
        self.debug: int = int(os.environ.get("DEBUG", 0))
        self.anthropic_model: str = os.environ.get("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")
        self.anthropic_max_tokens: int = int(os.environ.get("ANTHROPIC_MAX_TOKENS", 1024))
        self.llm_client_type: str = os.environ.get("LLM_CLIENT_TYPE", "anthropic")
