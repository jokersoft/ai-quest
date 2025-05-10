import uuid

import fastapi
from mangum import Mangum
from sqlalchemy.orm import Session

from app.clients import llm_client, db_client
from app.services import security
from app.services.story import StoryService
from app.schemas.story import FullStory
from app.schemas.message import Message
from app.schemas.user_decision import UserDecision

app = fastapi.FastAPI()
llm_client = llm_client.create_client()

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ask", dependencies=[fastapi.Depends(security.verify_api_key)])
def ask(question: str):
    response = llm_client.ask(question)
    return {"response": response}


@app.post("/story/init", response_model=FullStory, dependencies=[fastapi.Depends(security.verify_api_key)])
def init(db: Session = fastapi.Depends(db_client.get_db)) -> FullStory:
    story_service = StoryService(db)
    return story_service.init()


@app.get("/story/{story_id}", response_model=FullStory, dependencies=[fastapi.Depends(security.verify_api_key)])
def get(story_id: uuid.UUID, db: Session = fastapi.Depends(db_client.get_db)) -> FullStory:
    story_service = StoryService(db)
    return story_service.get(story_id)


@app.post("/story/{story_id}/act", response_model=FullStory, dependencies=[fastapi.Depends(security.verify_api_key)])
def act(story_id: uuid.UUID, user_decision: UserDecision, db: Session = fastapi.Depends(db_client.get_db)) -> FullStory:
    story_service = StoryService(db)
    return story_service.act(story_id, user_decision.message)


# for AWS Lambda compatibility:
handler = Mangum(app)
