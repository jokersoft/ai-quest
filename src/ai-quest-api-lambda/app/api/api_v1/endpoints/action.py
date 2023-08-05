from fastapi import APIRouter, HTTPException
from app.schema.action import Action
from app.config.openai import openai, configure_openai
from app.config.mysql import configure_mysql
from app.services.situation_content_provider import SituationContentProvider
from app.models.message import Message
from sqlalchemy.orm import Session
from uuid import uuid4


router = APIRouter()

@router.post("/")
async def action(action: Action):
    configure_openai()
    content_provider = SituationContentProvider()
    engine = configure_mysql()

    # Record the message in the database
    decision_message = Message(
        user_id=uuid4().bytes,  # TODO: unMock
        role='user',
        content=action.input,
        type='decision'
    )

    # TODO: Evaluate

    # Wrap and send to OpenAI
    system_message = content_provider.get_content('system')
    # https://platform.openai.com/docs/guides/gpt/chat-completions-api
    openai_response = openai.ChatCompletion.create(
            model="gpt-4-32k-0613",
            # TODO list messages
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": action.input},
            ],
            temperature=0.5,
            max_tokens=1000
    )
    response = openai_response.choices[0].message.content

    # TODO: parse the response into Outcome, Situation, Decisions

    # Record messages in the database
    situation_message = Message(
        user_id=uuid4().bytes,  # TODO: unMock
        role='user',
        content=response,
        type='situation' # TODO: unMock
    )

    # Create a new session
    with Session(engine) as session:
        session.add(decision_message)
        session.add(situation_message)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    # TODO: return based on response.choices[n].message.role
    return {"output": response}
