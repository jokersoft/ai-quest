from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, exc
from app.config.logger import configure_logger
from app.config.openai import configure_openai
from app.config.mysql import get_db
from app.services.storyteller_message_parser import StorytellerMessageParser
from app.repositories.action_repository import ActionRepository

router = APIRouter()


@router.get("/{thread_id}")
async def messages(thread_id: str, db: Session = Depends(get_db)):
    # TODO: move to constructor
    logger = configure_logger()
    client = configure_openai()
    storyteller_message_parser = StorytellerMessageParser()
    action_repository = ActionRepository(db)
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

            actions_texts = []
            for action_text in message_as_json.get('actions'):
                logger.debug('new action text:')
                logger.debug(action_text)
                actions_texts.append(action_text)
            actions = action_repository.add_all(last_message.id, actions_texts)

    logger.debug('Returned actions:')
    logger.debug(actions)
    logger.debug('action.text for action in actions:')
    logger.debug([action.text for action in actions])

    return {"messages": thread.data, "actions": [action.text for action in actions]}
