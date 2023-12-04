import json
from fastapi import APIRouter
from app.config.logger import configure_logger
from app.config.openai import configure_openai
from app.services.feedback_function_execution_service import FeedbackFunctionExecutionService

router = APIRouter()


@router.get("/{thread_id}/runs/{run_id}")
async def run(thread_id: str, run_id: str):

    # TODO: move to constructor
    logger = configure_logger()
    client = configure_openai()
    execution_service = FeedbackFunctionExecutionService()
    run_object = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )

    if run_object.status == 'requires_action':
        tool_calls = run_object.required_action.submit_tool_outputs.tool_calls
        for call in tool_calls:
            function_name = call.function.name
            function_arguments = json.loads(call.function.arguments)
            function_response = execution_service.execute(function_name, function_arguments)
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=[
                    {
                        "tool_call_id": call.id,
                        "output": function_response
                    }
                ]
            )

    return run_object
