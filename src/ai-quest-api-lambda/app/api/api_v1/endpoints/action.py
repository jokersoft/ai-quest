from fastapi import APIRouter
from app.schema.action import Action
from app.config.openai import openai, configure_openai


router = APIRouter()

@router.post("/")
async def action(action: Action):
    configure_openai()

    # https://platform.openai.com/docs/guides/gpt/chat-completions-api
    response = openai.ChatCompletion.create(
            model="gpt-4-32k-0613",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": action.input},
            ],
            temperature=0.5,
            max_tokens=1000
    )
    # TODO: return based on response.choices[n].message.role
    return {"output": response.choices[0].message.content.strip()}
