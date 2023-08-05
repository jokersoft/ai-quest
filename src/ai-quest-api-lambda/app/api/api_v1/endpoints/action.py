from fastapi import APIRouter
from app.schema.action import Action
from app.config.openai import openai, configure_openai
from app.services.situation_content_provider import SituationContentProvider


router = APIRouter()
content_provider = SituationContentProvider()

@router.post("/")
async def action(action: Action):
    configure_openai()

    system_message = content_provider.get_content('system')

    # https://platform.openai.com/docs/guides/gpt/chat-completions-api
    response = openai.ChatCompletion.create(
            model="gpt-4-32k-0613",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": action.input},
            ],
            temperature=0.5,
            max_tokens=1000
    )
    # TODO: return based on response.choices[n].message.role
    return {"output": response.choices[0].message.content.strip()}
