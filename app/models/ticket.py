from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TicketFaultType(StrEnum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    PRINTER = "printer"
    OTHER = "other"


class TicketPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(StrEnum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TicketAction(StrEnum):
    CREATE = "create"
    ASSIGN = "assign"
    START = "start"
    FINISH = "finish"
    CANCEL = "cancel"


class RepairResult(StrEnum):
    FIXED = "fixed"
    REPLACE_REPAIR = "replace_repair"
    SCRAPPED = "scrapped"
    UNRESOLVED = "unresolved"


class Ticket(Base):
    __tablename__ = "it_ticket"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    ticket_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    fault_type: Mapped[TicketFaultType | None] = mapped_column(String(50), default=None)
    priority: Mapped[TicketPriority] = mapped_column(String(20), default=TicketPriority.NORMAL)
    status: Mapped[TicketStatus] = mapped_column(String(30), default=TicketStatus.PENDING)
    reporter_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sys_user.id"))
    handler_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("sys_user.id"),
        default=None,
    )
    asset_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("it_asset.id"),
        default=None,
    )
    result: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    reporter = relationship(
        "User",
        back_populates="reported_tickets",
        foreign_keys=[reporter_id],
    )
    handler = relationship(
        "User",
        back_populates="handled_tickets",
        foreign_keys=[handler_id],
    )
    asset = relationship("Asset", back_populates="tickets")
    records = relationship("TicketRecord", back_populates="ticket")
    repair_records = relationship("RepairRecord", back_populates="ticket")


class TicketRecord(Base):
    __tablename__ = "it_ticket_record"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("it_ticket.id"))
    operator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sys_user.id"))
    from_status: Mapped[str | None] = mapped_column(String(30), default=None)
    to_status: Mapped[str] = mapped_column(String(30))
    action: Mapped[TicketAction] = mapped_column(String(50))
    remark: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ticket = relationship("Ticket", back_populates="records")
    operator = relationship("User", back_populates="ticket_records")


class RepairRecord(Base):
    __tablename__ = "it_repair_record"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("it_ticket.id"))
    asset_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("it_asset.id"))
    repair_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sys_user.id"))
    fault_reason: Mapped[str | None] = mapped_column(Text, default=None)
    repair_method: Mapped[str | None] = mapped_column(Text, default=None)
    repair_result: Mapped[RepairResult] = mapped_column(String(50))
    repair_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    repaired_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ticket = relationship("Ticket", back_populates="repair_records")
    asset = relationship("Asset", back_populates="repair_records")
    repair_user = relationship("User", back_populates="repair_records")
