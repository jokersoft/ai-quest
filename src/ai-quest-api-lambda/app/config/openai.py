import os
import json
import openai


def configure_openai():
    config = json.loads(os.environ["CONFIG"])
    openai.api_key = config["openai-api-key"]
