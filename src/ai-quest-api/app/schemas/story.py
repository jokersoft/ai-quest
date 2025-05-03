from pydantic import BaseModel


class Story(BaseModel):
    id: str
    user_id: str

    class Config:
        from_attributes = True
