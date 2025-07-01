from pydantic import BaseModel


class Chapter(BaseModel):
    id: str
    narration: str
    situation: str
    choices: list[str]
    action: str
    outcome: str
    number: int

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
