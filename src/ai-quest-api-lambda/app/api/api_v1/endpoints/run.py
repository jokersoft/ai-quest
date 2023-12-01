from fastapi import APIRouter
from app.config.logger import configure_logger
from app.config.openai import configure_openai

router = APIRouter()


@router.get("/{thread_id}/runs/{run_id}")
async def run(thread_id: str, run_id: str):

    # TODO: move to constructor
    logger = configure_logger()
    client = configure_openai()
    run_object = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )

    return run_object
