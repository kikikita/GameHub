from datetime import datetime
from pydantic import BaseModel


class SceneCreate(BaseModel):
    choice_text: str | None = None


class SceneOut(BaseModel):
    id: str
    description: str | None = None
    image_url: str | None = None
    choices_json: dict | None = None

    class Config:
        from_attributes = True

