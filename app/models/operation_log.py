from datetime import datetime
from enum import StrEnum

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OperationResult(StrEnum):
    SUCCESS = "success"
    FAIL = "fail"


class OperationLog(Base):
    __tablename__ = "sys_operation_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("sys_user.id"), default=None)
    module_name: Mapped[str] = mapped_column(String(100))
    operation_type: Mapped[str] = mapped_column(String(50))
    business_id: Mapped[int | None] = mapped_column(BigInteger, default=None)
    request_method: Mapped[str | None] = mapped_column(String(10), default=None)
    request_url: Mapped[str | None] = mapped_column(String(255), default=None)
    request_ip: Mapped[str | None] = mapped_column(String(50), default=None)
    operation_result: Mapped[OperationResult] = mapped_column(
        String(20),
        default=OperationResult.SUCCESS,
    )
    error_message: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="operation_logs")
