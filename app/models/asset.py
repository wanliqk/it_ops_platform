from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AssetStatus(StrEnum):
    IN_USE = "in_use"
    IDLE = "idle"
    REPAIRING = "repairing"
    SCRAPPED = "scrapped"


class AssetCategory(Base):
    __tablename__ = "it_asset_category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    category_name: Mapped[str] = mapped_column(String(100))
    category_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), default=None)
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    assets = relationship("Asset", back_populates="category")


class Asset(Base):
    __tablename__ = "it_asset"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    asset_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    asset_name: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("it_asset_category.id"))
    brand: Mapped[str | None] = mapped_column(String(50), default=None)
    model: Mapped[str | None] = mapped_column(String(100), default=None)
    serial_no: Mapped[str | None] = mapped_column(String(100), default=None)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("sys_user.id"), default=None)
    department: Mapped[str | None] = mapped_column(String(100), default=None)
    location: Mapped[str | None] = mapped_column(String(100), default=None)
    status: Mapped[AssetStatus] = mapped_column(String(30), default=AssetStatus.IN_USE)
    purchase_date: Mapped[date | None] = mapped_column(Date, default=None)
    warranty_expire_date: Mapped[date | None] = mapped_column(Date, default=None)
    remark: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    category = relationship("AssetCategory", back_populates="assets")
    user = relationship("User", back_populates="assets")
    tickets = relationship("Ticket", back_populates="asset")
    repair_records = relationship("RepairRecord", back_populates="asset")
