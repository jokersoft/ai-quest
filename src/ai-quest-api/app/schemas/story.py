from pydantic import BaseModel
from app.schemas import message

class Story(BaseModel):
    id: str
    user_id: str
    title: str | None = None

    class Config:
        from_attributes = True

class FullStory(Story):
    messages: list[message.Message]
