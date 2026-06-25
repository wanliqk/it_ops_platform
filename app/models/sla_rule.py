from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SlaRule(Base):
    __tablename__ = "it_sla_rule"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100))
    ticket_category: Mapped[str | None] = mapped_column(String(50), default=None)
    category_id: Mapped[int | None] = mapped_column(BigInteger, default=None, index=True)
    priority: Mapped[str] = mapped_column(String(20), index=True)
    response_minutes: Mapped[int] = mapped_column(Integer)
    resolve_minutes: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[int] = mapped_column(SmallInteger, default=1, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
