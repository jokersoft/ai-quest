from fastapi import APIRouter
from app.config.logger import configure_logger
from app.config.openai import configure_openai
from app.services.storyteller_message_parser import StorytellerMessageParser
from app.repositories.action_repository import ActionRepository

router = APIRouter()


@router.get("/{thread_id}")
async def messages(thread_id: str):
    # TODO: move to constructor
    logger = configure_logger()
    configure_openai()
    client = configure_openai()
    storyteller_message_parser = StorytellerMessageParser()
    action_repository = ActionRepository()
    thread = client.beta.threads.messages.list(thread_id=thread_id)
    actions = []

    logger.debug('last message:')
    logger.debug(thread.data[0])
    if thread.data and thread.data[0].role == 'assistant':
        last_message = thread.data[0]

        # TODO: actionsProvider with cache layer in DB
        actions = action_repository.get(last_message.id)
        if not actions:
            message_as_json = storyteller_message_parser.get_as_json(last_message.content[0].text.value)
            logger.debug('message_as_json:')
            logger.debug(message_as_json)

            for action_text in message_as_json.get('actions'):
                logger.debug('new action:')
                logger.debug(action_text)
                action = action_repository.add(last_message.id, action_text)
                actions.append(action)

    return {"messages": thread.data, "actions": [action.get('text') for action in actions]}
