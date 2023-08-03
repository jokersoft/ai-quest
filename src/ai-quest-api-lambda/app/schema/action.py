from pydantic import BaseModel


class Action(BaseModel):
    input: str
