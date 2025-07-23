import uuid
from datetime import datetime

from sqlalchemy import Boolean, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tg_id: Mapped[str] = mapped_column(Text, unique=True)
    username: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    templates: Mapped[list["GameTemplate"]] = relationship(back_populates="user")
    sessions: Mapped[list["GameSession"]] = relationship(back_populates="user")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, tg_id={self.tg_id})"

