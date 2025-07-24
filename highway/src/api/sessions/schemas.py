from datetime import datetime
from pydantic import BaseModel


class SessionCreate(BaseModel):
    template_id: str | None = None


class SessionOut(BaseModel):
    id: str
    started_at: datetime
    share_code: str

    class Config:
        from_attributes = True

