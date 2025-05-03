from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str

    class Config:
        from_attributes = True
