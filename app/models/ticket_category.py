from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TicketCategory(Base):
    __tablename__ = "it_ticket_category"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
    )
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("it_ticket_category.id"),
        default=None,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), default=None)
    default_priority: Mapped[str | None] = mapped_column(String(20), default=None)
    default_group_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("it_work_group.id"),
        default=None,
        index=True,
    )
    assignment_strategy: Mapped[str | None] = mapped_column(String(30), default=None)
    fixed_assignee_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("sys_user.id"),
        default=None,
        index=True,
    )
    require_asset: Mapped[int] = mapped_column(SmallInteger, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    parent = relationship("TicketCategory", remote_side=[id])
    default_group = relationship("WorkGroup")
    fixed_assignee = relationship("User")
