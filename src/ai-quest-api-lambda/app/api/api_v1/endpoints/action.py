from fastapi import APIRouter
from app.schema.action import Action
from app.config.openai import configure_openai
from app.config.logger import configure_logger
from app.config.openai_tools_configs import tools
from app.services.situation_content_provider import SituationContentProvider
from uuid import UUID

# TODO: unMock IDs
assistant_id = 'asst_A4n3KrD5aopvdfYrlqDJF1An'
uuid_string = '3c627569-6c74-2d69-6e20-6d6574686f64'
user_uuid = UUID(uuid_string)

router = APIRouter()


@router.post("/")
async def action(action: Action):
    # TODO: move to constructor
    logger = configure_logger()
    content_provider = SituationContentProvider()
    client = configure_openai()
    client.beta.threads.messages.create(
        thread_id=action.thread_id,
        content=action.message,
        role='user',
    )

    # TODO: persistance here

    # TODO: function calling

    system_message = content_provider.get_content('system')
    # https://platform.openai.com/docs/guides/function-calling/parallel-function-calling
    run = client.beta.threads.runs.create(
        thread_id=action.thread_id,
        assistant_id=assistant_id,
        model="gpt-4-1106-preview",
        instructions=system_message,
        tools=tools,
    )

    return {"run_id": run.id, "run_status": run.status}
