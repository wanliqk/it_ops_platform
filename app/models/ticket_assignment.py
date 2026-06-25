from datetime import datetime
from enum import StrEnum

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TicketAssignType(StrEnum):
    MANUAL = "manual"
    AUTO = "auto"
    CLAIM = "claim"


class TicketAssignStrategy(StrEnum):
    LEAST_WORKLOAD = "least_workload"
    FIXED_USER = "fixed_user"


class TicketAssignmentRule(Base):
    __tablename__ = "ticket_assignment_rule"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[int | None] = mapped_column(BigInteger, default=None, index=True)
    priority: Mapped[str | None] = mapped_column(String(20), default=None, index=True)
    ops_group_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("it_work_group.id"),
        default=None,
        index=True,
    )
    assign_strategy: Mapped[TicketAssignStrategy] = mapped_column(String(30))
    target_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("sys_user.id"),
        default=None,
        index=True,
    )
    enabled: Mapped[int] = mapped_column(SmallInteger, default=1, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=100, index=True)
    remark: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    ops_group = relationship("WorkGroup")
    target_user = relationship("User")


class TicketAssignmentLog(Base):
    __tablename__ = "ticket_assignment_log"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
    )
    ticket_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("it_ticket.id"), index=True)
    rule_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("ticket_assignment_rule.id"),
        default=None,
        index=True,
    )
    ops_group_id: Mapped[int | None] = mapped_column(BigInteger, default=None)
    assignee_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("sys_user.id"),
        default=None,
        index=True,
    )
    assign_type: Mapped[str | None] = mapped_column(String(30), default=None)
    assign_strategy: Mapped[str | None] = mapped_column(String(30), default=None)
    success: Mapped[int] = mapped_column(SmallInteger, default=0, index=True)
    fail_stage: Mapped[str | None] = mapped_column(String(50), default=None)
    fail_reason: Mapped[str | None] = mapped_column(String(255), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    ticket = relationship("Ticket")
    rule = relationship("TicketAssignmentRule")
    assignee = relationship("User")
