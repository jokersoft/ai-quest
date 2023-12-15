import os
import json
from openai import OpenAI


def configure_openai():
    config = json.loads(os.environ["CONFIG"])
    return OpenAI(api_key=config["openai-api-key"])
