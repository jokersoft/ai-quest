from fastapi import APIRouter
from app.config.openai import openai, configure_openai
from app.config.logger import configure_logger

router = APIRouter()


@router.post("/")
async def init():
    # TODO: move to constructor
    client = configure_openai()
    logger = configure_logger()
    logger.info(f"creating a thread")

    # https://platform.openai.com/docs/assistants/how-it-works/managing-threads-and-messages
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Hello?",
            }
        ]
    )

    return {"thread_id": thread.id}
