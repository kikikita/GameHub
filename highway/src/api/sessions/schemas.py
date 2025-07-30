from datetime import datetime
from pydantic import BaseModel


class SessionCreate(BaseModel):
    story_id: str | None = None


class SessionOut(BaseModel):
    id: str
    started_at: datetime
    share_code: str
    story_frame: dict | None = None
    is_finished: bool | None = None

    class Config:
        from_attributes = True
