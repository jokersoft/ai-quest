from fastapi import APIRouter, HTTPException
from app.schema.action import Action
from app.config.openai import openai, configure_openai
from app.config.logger import configure_logger
from app.services.situation_content_provider import SituationContentProvider
from app.models.message import Message
from app.repositories.message_repository import MessageRepository
from uuid import uuid4, UUID

# TODO: unMock user_id
uuid_string = '3c627569-6c74-2d69-6e20-6d6574686f64';
user_uuid = UUID(uuid_string)

router = APIRouter()

@router.post("/")
async def action(action: Action):
    # TODO: move to Container (or to global scope?)
    configure_openai()
    content_provider = SituationContentProvider()
    message_repository = MessageRepository()
    logger = configure_logger()

    previous_messages = message_repository.get_messages_by_user_id(user_uuid)

    # Record the message in the database
    decision_message = Message(
        id=uuid4().bytes,
        user_id=user_uuid.bytes,
        role='user',
        content=action.input,
        type='decision'
    )
    logger.info("decision_message recorded")

    # TODO: Evaluate

    # Wrap and send to OpenAI
    system_message = content_provider.get_content('system')
    # https://platform.openai.com/docs/guides/gpt/chat-completions-api
    openai_response = openai.ChatCompletion.create(
            model="gpt-4-32k-0613",
            # TODO list messages
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": action.input},
            ],
            temperature=0.5,
            max_tokens=1000
    )
    response = openai_response.choices[0].message.content

    # TODO: parse the response into Outcome, Situation, Decisions

    # Record messages in the database
    situation_message = Message(
        id=uuid4().bytes,
        user_id=user_uuid.bytes,
        role='user',
        content=response,
        type='situation' # TODO: unMock
    )
    logger.info("situation_message recorded")

    message_repository.add_message(decision_message)
    message_repository.add_message(situation_message)

    # TODO: return based on response.choices[n].message.role
    return {"output": response}
