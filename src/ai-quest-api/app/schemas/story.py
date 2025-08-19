from pydantic import BaseModel, Field, field_validator
from typing import Union
import uuid


class Chapter(BaseModel):
    id: Union[str, bytes, uuid.UUID] = Field(alias='id')
    story_id: Union[str, bytes, uuid.UUID] = Field(alias='story_id')
    narration: str
    situation: str
    choices: list[str]
    action: str
    outcome: str
    number: int

    @field_validator('id', mode='before')
    def convert_id(cls, v: Union[bytes, uuid.UUID, str]) -> str:
        if isinstance(v, bytes):
            return str(uuid.UUID(bytes=v))
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class Story(BaseModel):
    id: Union[str, bytes, uuid.UUID] = Field(alias='id')
    user_id: Union[str, bytes, uuid.UUID] = Field(alias='user_id')
    title: str | None = None

    @field_validator('id', 'user_id', mode='before')
    def convert_id(cls, v: Union[bytes, uuid.UUID, str]) -> str:
        if isinstance(v, bytes):
            return str(uuid.UUID(bytes=v))
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class FullStory(Story):
    chapters: list[Chapter]
    current_choices: list[str]
