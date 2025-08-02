"""BundlePurchase model representing history of bundle purchases."""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class BundlePurchase(Base):
    """Stores information about user bundle purchases.\n\n    A record is created when the user initiates a bundle purchase via the \n    /api/v1/wishes/subscribe/ endpoint. The record remains in *pending* state \n    until the payment is verified and confirmed by Telegram payment webhook\n    handlers (\"/bundle/verify\" and \"/bundle/confirm\" endpoints).\n    """

    __tablename__ = "bundle_purchases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    bundle: Mapped[str] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(Text, nullable=True)
    purchased_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
    )
    invoice_payload: Mapped[str | None] = mapped_column(
        Text, nullable=True, index=True
    )

    # ORM relationship back to the owning user
    user: Mapped["User"] = relationship(back_populates="bundle_purchases")

    def __repr__(self) -> str:
        return (
            f"BundlePurchase(id={self.id}, user_id={self.user_id}, bundle={self.bundle}, "
            f"status={self.status})"
        )
