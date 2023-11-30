from fastapi import APIRouter
from app.config.openai import configure_openai
from app.config.logger import configure_logger
from app.services.situation_content_provider import SituationContentProvider

router = APIRouter()

# TODO: unMock IDs
assistant_id = 'asst_A4n3KrD5aopvdfYrlqDJF1An'


@router.post("/")
async def init():
    # TODO: move to constructor
    client = configure_openai()
    content_provider = SituationContentProvider()
    logger = configure_logger()
    logger.info(f"creating a thread")

    system_message = content_provider.get_content('system')

    # https://platform.openai.com/docs/assistants/how-it-works/managing-threads-and-messages
    run = client.beta.threads.create_and_run(
        assistant_id=assistant_id,
        thread={
            "messages": [
                {"role": "user", "content": "Hello?"}
            ]
        },
        instructions=system_message
    )

    return {"thread_id": run.thread_id, "run_id": run.id}
