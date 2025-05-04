import fastapi
from mangum import Mangum
from sqlalchemy.orm import Session

from app.clients import llm_client, db_client
from app.entities.message import Message
from app.entities.story import Story
from app.services.story import StoryService
from app.schemas.story import Story
from app.schemas.message import Message

app = fastapi.FastAPI()
llm_client = llm_client.create_client()

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ask")
def ask(question: str):
    response = llm_client.ask(question)
    return {"response": response}


@app.post("/init", response_model=tuple[Story, list[Message]])
def init(db: Session = fastapi.Depends(db_client.get_db)) -> tuple[Story, list[Message]]:
    story_service = StoryService(db)
    story, messages = story_service.init_story()

    return story, messages


@app.post("/act")
def init(action: str):
    # TODO
    raise NotImplemented()

# for AWS Lambda compatibility:
handler = Mangum(app)
