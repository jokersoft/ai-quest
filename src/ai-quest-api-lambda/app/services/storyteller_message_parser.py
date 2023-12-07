import json
from sqlalchemy.orm import Session
from app.config.logger import configure_logger
from app.config.mysql import configure_mysql
from app.config.openai import configure_openai
from app.services.situation_content_provider import SituationContentProvider


class StorytellerMessageParser:
    def __init__(self):
        engine = configure_mysql()
        self.session = Session(engine)
        self.logger = configure_logger()
        self.openaiClient = configure_openai()
        self.content_provider = SituationContentProvider()

    # call only if no cache! (in DB)
    def get_as_json(self, message):
        self.logger.debug(f"Parsing Actions from the message:")
        system_message = self.content_provider.get_content('storyteller_message_parser')
        response = self.openaiClient.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ]
        )
        json_string = response.choices[0].message.content
        self.logger.debug(f"JSON: {json_string}")

        return json.loads(json_string)
