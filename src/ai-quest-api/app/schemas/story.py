from pydantic import BaseModel, field_validator
import uuid


class Chapter(BaseModel):
    id: str
    narration: str
    situation: str
    choices: list[str]
    action: str
    outcome: str
    number: int

    @field_validator('id', mode='before')
    def convert_id(cls, v):
        if isinstance(v, bytes):
            return str(uuid.UUID(bytes=v))
        return v

    class Config:
        from_attributes = True


class Story(BaseModel):
    id: str
    user_id: str
    title: str | None = None

    class Config:
        from_attributes = True


class FullStory(Story):
    chapters: list[Chapter]
