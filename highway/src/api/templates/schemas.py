from datetime import datetime
from pydantic import BaseModel


class TemplateCreate(BaseModel):
    title: str | None = None
    setting_desc: str | None = None
    char_name: str | None = None
    char_age: str | None = None
    char_background: str | None = None
    char_personality: str | None = None
    genre: str | None = None
    story_frame: dict | None = None
    is_free: bool | None = None
    is_preset: bool | None = None


class TemplateOut(TemplateCreate):
    id: str
    is_public: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateShareOut(BaseModel):
    id: str
    share_code: str

