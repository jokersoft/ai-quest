from pydantic import BaseModel


class UserDecision(BaseModel):
    message: str

    class Config:
        from_attributes = True
