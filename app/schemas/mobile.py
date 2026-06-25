from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.models.faq import FaqCategory
from app.models.ticket import TicketAction, TicketPriority, TicketStatus
from app.models.user import UserRole

T = TypeVar("T")


class MobileResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T | None = None


class OptionItem(BaseModel):
    label: str
    value: str


class MobileUserRead(BaseModel):
    id: int
    username: str
    real_name: str
    role: UserRole
    department: str | None = None
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MobileLoginRequest(BaseModel):
    username: str
    password: str


class MobileLoginData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: MobileUserRead


class TicketSummaryData(BaseModel):
    total_count: int
    pending_count: int
    assigned_count: int
    processing_count: int
    completed_count: int
    cancelled_count: int


class MobileAssetOption(BaseModel):
    id: int
    asset_no: str
    asset_name: str
    brand: str | None = None
    model: str | None = None
    status: str
    location: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TicketFormOptionsData(BaseModel):
    categories: list[OptionItem]
    priorities: list[OptionItem]


class MobileTicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    category_id: int
    priority: TicketPriority = TicketPriority.NORMAL
    asset_id: int | None = None


class MobileTicketCreated(BaseModel):
    id: int
    ticket_no: str
    title: str
    status: TicketStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MobileTicketListItem(MobileTicketCreated):
    category_id: int
    priority: TicketPriority
    asset_id: int | None = None


class PageData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class MobileTicketUser(BaseModel):
    id: int
    username: str
    real_name: str
    department: str | None = None
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MobileTicketAsset(BaseModel):
    id: int
    asset_no: str
    asset_name: str
    brand: str | None = None
    model: str | None = None
    serial_no: str | None = None
    location: str | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class MobileTicketRecordRead(BaseModel):
    id: int
    action: TicketAction
    from_status: str | None = None
    to_status: str
    remark: str | None = None
    operator: MobileTicketUser | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MobileRepairRecordRead(BaseModel):
    id: int
    fault_reason: str | None = None
    repair_method: str | None = None
    repair_result: str
    repair_cost: Any
    repaired_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MobileTicketDetail(BaseModel):
    id: int
    ticket_no: str
    title: str
    description: str
    category_id: int
    priority: TicketPriority
    status: TicketStatus
    result: str | None = None
    reporter: MobileTicketUser
    handler: MobileTicketUser | None = None
    asset: MobileTicketAsset | None = None
    repair_records: list[MobileRepairRecordRead]
    records: list[MobileTicketRecordRead]
    created_at: datetime
    assigned_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MobileTicketCancelRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=255)


class MobileTicketCancelled(BaseModel):
    id: int
    ticket_no: str
    status: TicketStatus

    model_config = ConfigDict(from_attributes=True)


class FaqListItem(BaseModel):
    id: int
    title: str
    category: FaqCategory
    summary: str | None = None
    view_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FaqDetail(FaqListItem):
    content: str
