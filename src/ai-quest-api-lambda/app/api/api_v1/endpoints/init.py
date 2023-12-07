from fastapi import APIRouter
from app.config.openai import configure_openai
from app.config.logger import configure_logger

router = APIRouter()

# TODO: unMock IDs
assistant_id = 'asst_GNZn6y1f1OE8F9CA62AlvEfn'


@router.post("/")
async def init():
    # TODO: move to constructor
    client = configure_openai()
    logger = configure_logger()
    logger.info(f"creating a thread")

    # https://platform.openai.com/docs/assistants/how-it-works/managing-threads-and-messages
    run = client.beta.threads.create_and_run(
        assistant_id=assistant_id,
        thread={
            "messages": [
                {"role": "user", "content": "Where am I?"}
            ]
        },
    )

    return {"thread_id": run.thread_id, "run_id": run.id, "run_status": run.status}
