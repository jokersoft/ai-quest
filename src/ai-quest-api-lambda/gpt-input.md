These are files of a python project:

`./app/main.py`:
```
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.api.api_v1.api import router as api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # warning!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "root"}

app.include_router(api_router, prefix="/api/v1")

# for AWS Lambda compatibility:
handler = Mangum(app)
```

`./app/config/logger.py`:
```
import os
import sys
import logging


def configure_logger():
    DEBUG = int(os.environ["DEBUG"])
    logging.basicConfig(stream=sys.stdout)
    logger = logging.getLogger()
    if DEBUG == 1:
        logger.setLevel(logging.DEBUG)
        logger.debug("DEBUG mode enabled")
    else:
        logger.setLevel(logging.INFO)
    return logger

```

`./app/config/openai.py`:
```
import os
import json
import openai


def configure_openai():
    config = json.loads(os.environ["CONFIG"])
    openai.api_key = config["openai-api-key"]
```

`./app/config/mysql.py`:
```
import os
import json
from sqlalchemy import create_engine


def configure_mysql():
    DEBUG = int(os.environ["DEBUG"])
    config = json.loads(os.environ["CONFIG"])
    # mysql+pymysql://user:password@localhost/dbname
    engine = create_engine(config["db-credentials"], echo=(DEBUG == 1))
    return engine
```

`./app/repositories/message_repository.py`:
```
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.logger import configure_logger
from app.config.mysql import configure_mysql
from app.models.message import Message
from uuid import UUID


class MessageRepository:
    def __init__(self):
        engine = configure_mysql()
        self.session = Session(engine)
        self.logger = configure_logger()

    def get_messages_by_user_id(self, user_id: UUID):
        sql = text("SELECT * FROM messages WHERE user_id = UUID_TO_BIN(:user_id) ORDER BY timestamp DESC")
        result = self.session.execute(sql, {'user_id': user_id.hex})
        messages = result.fetchall()

        self.logger.debug(f"Retrieved {len(messages)} messages for user_id {user_id}")
        return messages

    def add_message(self, message: Message):
        self.logger.debug(f"Adding message {message.id} for user_id {message.user_id}")
        self.session.add(message)
        self.session.commit()
```

`./app/models/user.py`:
```
from sqlalchemy import Column, String, Uuid
from sqlalchemy.orm import declarative_base
from uuid import uuid4

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4())
    name = Column(String(50))
    email = Column(String(50))
```

`./app/models/event.py`:
```
from sqlalchemy import Column, String, Integer, DateTime, Uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from uuid import uuid4

Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4())
    subject = Column(String(100))
    delta = Column(Integer())
    reason = Column(String(1000))
    impact = Column(String(1000))
    timestamp = Column(DateTime(timezone=True), default=func.now())
```

`./app/models/message.py`:
```
from sqlalchemy import Column, String, DateTime, Uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from uuid import uuid4

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4())
    user_id = Column(Uuid(as_uuid=True), index=True)
    role = Column(String(50))
    content = Column(String(1000))
    type = Column(String(50))
    timestamp = Column(DateTime(timezone=True), default=func.now())
```

`./app/schema/action.py`:
```
from pydantic import BaseModel


class Action(BaseModel):
    input: str
```

`./app/api/api_v1/api.py`:
```
from fastapi import APIRouter

from .endpoints import action

router = APIRouter()
router.include_router(action.router, prefix="/action", tags=["Action"])
```

`./app/api/api_v1/endpoints/action.py`:
```
import json
from fastapi import APIRouter, HTTPException
from app.schema.action import Action
from app.config.openai import openai, configure_openai
from app.config.logger import configure_logger
from app.services.feedback_function_execution_service import FeedbackFunctionExecutionService
from app.services.situation_content_provider import SituationContentProvider
from app.models.message import Message
from app.repositories.message_repository import MessageRepository
from uuid import uuid4, UUID

# TODO: unMock user_id
uuid_string = '3c627569-6c74-2d69-6e20-6d6574686f64'
user_uuid = UUID(uuid_string)

router = APIRouter()


@router.post("/")
async def action(action: Action):
    # TODO: move to Container (or to global scope?)
    configure_openai()
    content_provider = SituationContentProvider()
    message_repository = MessageRepository()
    logger = configure_logger()

    previous_messages = message_repository.get_messages_by_user_id(user_uuid)
    previous_messages_formatted = [{"role": msg.role, "content": msg.content} for msg in previous_messages]
    logger.info(f"previous_messages count: {len(previous_messages)}")

    # Record the message in the database
    decision_message = Message(
        id=uuid4().bytes,
        user_id=user_uuid.bytes,
        role='user',
        content=action.input,
        type='decision'
    )
    logger.info("decision_message recorded")

    # TODO: Evaluate

    # Wrap and send to OpenAI
    system_message = content_provider.get_content('system')
    # https://platform.openai.com/docs/guides/gpt/chat-completions-api
    openai_response = openai.ChatCompletion.create(
            model="gpt-4-32k-0613",
            # Order is: system message, previous_messages_formatted, latest user input
            messages=[
                {"role": "system", "content": system_message},
            ] + previous_messages_formatted + [
                {"role": "user", "content": action.input},
            ],
            temperature=0.5,
            max_tokens=1000
    )
    situation = openai_response.choices[0].message.content
    function_call =  openai_response.choices[0].message.get("function_call")
    if function_call:
        logger.debug(f"function_call: {function_call.arguments}")
        name = function_call.name
        arguments = json.loads(function_call.arguments)
        FeedbackFunctionExecutionService.execute(name, arguments)

    # TODO: parse the response into Outcome, Situation, Choice, Decision

    # Record messages in the database
    situation_message = Message(
        id=uuid4().bytes,
        user_id=user_uuid.bytes,
        role='user',
        content=situation,
        type='situation' # TODO: unMock
    )
    logger.info("situation_message recorded")

    message_repository.add_message(decision_message)
    message_repository.add_message(situation_message)

    # Add the OpenAI response to the messages list
    return_messages = previous_messages_formatted + [
        {"role": "user", "content": action.input},
        {"role": "assistant", "content": situation}
    ]

    # TODO: return based on response.choices[n].message.role
    return {"messages": return_messages}
```

`./app/services/player_health_service.py`:
```
from sqlalchemy.orm import Session
from app.config.logger import configure_logger
from app.config.mysql import configure_mysql
from app.models.user import User
from app.models.event import Event

class PlayerHealthService:
    def __init__(self):
        engine = configure_mysql()
        self.session = Session(engine)
        self.logger = configure_logger()

    def update_player_health(self, user_id, delta, reason, impact):
        self.logger.debug(f"Recording health change: {user_id}, {delta}, {reason}, {impact}")
        # Record the health update event
        # event = Event(user_id=user_id, delta=delta, reason=reason, impact=impact)
        # self.session.add(event)

        # Update the player's health
        # user = self.session.query(User).filter(User.id == user_id).one()
        # user.health += delta

        # self.session.commit()
```

`./app/services/situation_content_provider.py`:
```
import os

class SituationContentProvider:
    def __init__(self):
        self.situation_to_file_map = {
            "system": "./app/data/prompts/system.txt",
        }

    def get_content(self, situation: str) -> str:
        file_path = self.situation_to_file_map.get(situation)
        if file_path and os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                return file.read().strip()
        else:
            raise ValueError(f"No file found for situation: {situation} {os.getcwd()}")
```

`./app/services/feedback_function_execution_service.py`:
```
import json
from app.config.logger import configure_logger
from app.services.player_health_service import PlayerHealthService

class FeedbackFunctionExecutionService:
    def __init__(self):
        self.player_health_service = PlayerHealthService()
        with open('./app/data/multi_function_call.json', 'r') as file:
            self.functions = file.read().strip()

        self.available_functions = []
        for function in self.functions:
            if function['name'] == 'multi_function':
                self.available_functions.extend(function['parameters']['properties'].keys())
        self.logger = configure_logger()

    def execute(self, function_name, arguments):
        for available_function_name in self.available_functions:
            if function_name == available_function_name:
                function_name(**arguments)

        raise ValueError(f"No function found for name: {function_call.name}")
```

`./tests/test_action.py`:
```
from unittest import mock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@mock.patch('app.api.api_v1.api.action.MessageRepository')
@mock.patch('app.api.api_v1.api.action.SituationContentProvider.get_content')
@mock.patch('app.api.api_v1.api.action.openai.ChatCompletion.create')
def test_action(mock_create, mock_get_content, mock_repo):
    mock_message = mock.Mock()
    mock_message.role = 'system'
    mock_message.content = 'test completion'

    mock_choice = mock.Mock()
    mock_choice.message = mock_message
    # TODO
    # mock_choice.message.get.return_value = mock.Mock(arguments='{"temperature": "22", "unit": "celsius", "description": "Sunny"}')
    mock_choice.message.get.return_value = None
    mock_create.return_value = mock.Mock(choices=[mock_choice])

    # Mock the get_content method to return a test system message
    mock_get_content.return_value = 'You are a helpful assistant.'

    # Mock the repository's methods
    mock_repo.return_value.get_messages_by_user_id.return_value = []
    mock_repo.return_value.add_message.return_value = None

    with mock.patch.dict('os.environ', {'DEBUG': '1', 'CONFIG': '{"openai-api-key":"test", "db-credentials":"mysql+pymysql://user:password@localhost/dbname"}'}):
        response = client.post("/api/v1/action/", json={"input": "example input"})
        assert response.status_code == 200
        assert response.json() == {"messages": [
            {"role": "user", "content": "example input"},
            {"role": "assistant", "content": "test completion"}
        ]}

    # Assert that the repository's add_message and session's commit methods were called
    mock_repo.return_value.get_messages_by_user_id.assert_called_once()
    mock_repo.return_value.add_message.assert_called()

    # Assert that openai.ChatCompletion.create was called with the correct messages
    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "example input"},
    ]
    mock_create.assert_called_once_with(
        model="gpt-4-32k-0613",
        messages=expected_messages,
        temperature=0.5,
        max_tokens=1000
    )```
