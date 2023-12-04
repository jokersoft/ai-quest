from pydantic import BaseModel


class Action(BaseModel):
    message: str
    thread_id: str
