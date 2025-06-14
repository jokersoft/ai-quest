import logging
import uuid

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from sqlalchemy.orm import Session

from app.clients import llm_client, db_client
from app.services import security
from app.services import user
from app.services.story import StoryService
from app.schemas.story import Story, FullStory
from app.schemas.user_decision import UserDecision

API_GATEWAY_BASE_PATH = "/quest"

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this to your specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

llm_client = llm_client.create_client()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ask", dependencies=[fastapi.Depends(security.verify_api_key)])
def ask(question: str):
    response = llm_client.ask(question)
    return {"response": response}


@app.get("/stories", dependencies=[fastapi.Depends(security.verify_api_key)])
def stories(
    user_info: user.UserInfo = fastapi.Depends(user.get_user_info),
    db: Session = fastapi.Depends(db_client.get_db)
) -> list[Story]:
    logger.info(f"User {user_info.email} requesting stories.")
    stories = StoryService(db).list(user_info)
    return stories


@app.post("/story/init", response_model=FullStory, dependencies=[fastapi.Depends(security.verify_api_key)])
def init(
    user_info: user.UserInfo = fastapi.Depends(user.get_user_info),
    db: Session = fastapi.Depends(db_client.get_db)
) -> FullStory:
    story_service = StoryService(db)
    new_story = story_service.init(user_info)
    logger.info(f"New Story {new_story.id} created")
    return new_story


@app.get("/story/{story_id}", response_model=FullStory, dependencies=[fastapi.Depends(security.verify_api_key)])
def get(story_id: uuid.UUID, db: Session = fastapi.Depends(db_client.get_db)) -> FullStory:
    logger.debug(f"Retrieving Story {story_id}")
    story_service = StoryService(db)
    return story_service.get(story_id)


@app.post("/story/{story_id}/act", response_model=FullStory, dependencies=[fastapi.Depends(security.verify_api_key)])
def act(story_id: uuid.UUID, user_decision: UserDecision, db: Session = fastapi.Depends(db_client.get_db)) -> FullStory:
    logger.debug(f"Acting inside Story {story_id}")
    story_service = StoryService(db)
    return story_service.act(story_id, user_decision.message)


# for AWS Lambda compatibility:
handler = Mangum(app, api_gateway_base_path=API_GATEWAY_BASE_PATH)
