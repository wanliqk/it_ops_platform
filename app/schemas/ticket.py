from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.ticket import (
    RepairResult,
    TicketAction,
    TicketFaultType,
    TicketPriority,
    TicketStatus,
)


class TicketBase(BaseModel):
    title: str
    description: str
    fault_type: TicketFaultType | None = None
    priority: TicketPriority = TicketPriority.NORMAL
    reporter_id: int | None = None
    handler_id: int | None = None
    asset_id: int | None = None
    result: str | None = None


class TicketCreate(TicketBase):
    ticket_no: str | None = None


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    fault_type: TicketFaultType | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    handler_id: int | None = None
    asset_id: int | None = None
    result: str | None = None
    assigned_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class TicketAssign(BaseModel):
    handler_id: int
    remark: str | None = None


class TicketStart(BaseModel):
    remark: str | None = None


class TicketComplete(BaseModel):
    result: str
    fault_reason: str | None = None
    repair_method: str | None = None
    repair_result: RepairResult
    repair_cost: Decimal = Decimal("0.00")
    asset_status_after_repair: str | None = None
    remark: str | None = None


class TicketCancel(BaseModel):
    reason: str | None = None


class TicketRead(TicketBase):
    id: int
    ticket_no: str
    status: TicketStatus
    created_at: datetime
    assigned_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    sla_response_deadline: datetime | None
    sla_resolve_deadline: datetime | None
    first_response_at: datetime | None
    resolved_at: datetime | None
    response_overdue: int
    resolve_overdue: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketRecordBase(BaseModel):
    ticket_id: int
    operator_id: int
    from_status: str | None = None
    to_status: str
    action: TicketAction
    remark: str | None = None


class TicketRecordCreate(TicketRecordBase):
    pass


class TicketRecordRead(TicketRecordBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RepairRecordBase(BaseModel):
    ticket_id: int
    asset_id: int
    repair_user_id: int
    fault_reason: str | None = None
    repair_method: str | None = None
    repair_result: RepairResult
    repair_cost: Decimal = Decimal("0.00")
    repaired_at: datetime


class RepairRecordCreate(RepairRecordBase):
    pass


class RepairRecordUpdate(BaseModel):
    fault_reason: str | None = None
    repair_method: str | None = None
    repair_result: RepairResult | None = None
    repair_cost: Decimal | None = None
    repaired_at: datetime | None = None


class RepairRecordRead(RepairRecordBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
