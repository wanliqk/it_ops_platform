from datetime import datetime
from enum import StrEnum

from sqlalchemy import BigInteger, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(StrEnum):
    ADMIN = "admin"
    IT_STAFF = "it_staff"
    EMPLOYEE = "employee"


class User(Base):
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    real_name: Mapped[str] = mapped_column(String(50))
    role: Mapped[UserRole] = mapped_column(String(30))
    department: Mapped[str | None] = mapped_column(String(100), default=None)
    phone: Mapped[str | None] = mapped_column(String(30), default=None)
    email: Mapped[str | None] = mapped_column(String(100), default=None)
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    reported_tickets = relationship(
        "Ticket",
        back_populates="reporter",
        foreign_keys="Ticket.reporter_id",
    )
    handled_tickets = relationship(
        "Ticket",
        back_populates="handler",
        foreign_keys="Ticket.handler_id",
    )
    assets = relationship("Asset", back_populates="user")
    ticket_records = relationship("TicketRecord", back_populates="operator")
    repair_records = relationship("RepairRecord", back_populates="repair_user")
    operation_logs = relationship("OperationLog", back_populates="user")
