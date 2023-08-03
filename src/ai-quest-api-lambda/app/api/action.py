from fastapi import APIRouter
from app.schema.action import Action

router = APIRouter()


@router.post("/api/v1/action/")
async def perform_action(action: Action):
    # Perform some action here...
    # For now, let's just return the input we received.
    return {"input": action.input}
