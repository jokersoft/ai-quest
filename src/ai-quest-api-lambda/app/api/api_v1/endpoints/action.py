from fastapi import APIRouter
from app.schema.action import Action
from app.config.openai import openai, configure_openai


router = APIRouter()

@router.post("/")
async def action(action: Action):
    configure_openai()
    response = openai.Completion.create(
            engine="gpt-4-32k-0613",
            prompt=action.input,
            temperature=0.5,
            max_tokens=1000
    )
    return {"output": response.choices[0].text.strip()}
