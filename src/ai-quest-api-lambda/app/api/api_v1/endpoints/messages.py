from fastapi import APIRouter
from app.config.logger import configure_logger
from app.config.openai import openai, configure_openai

router = APIRouter()


@router.get("/{thread_id}")
async def messages(thread_id: str):
    # TODO: move to constructor
    logger = configure_logger()
    configure_openai()
    client = configure_openai()
    thread = client.beta.threads.messages.list(thread_id=thread_id)

    # TODO: parse properly
    return {"messages": thread}
