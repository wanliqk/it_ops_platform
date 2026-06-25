from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

AssignmentStrategy = Literal["least_workload", "fixed_user"]
DefaultPriority = Literal["low", "medium", "normal", "high", "urgent"]


class TicketCategoryBase(BaseModel):
    parent_id: int | None = None
    name: str
    code: str
    description: str | None = None
    default_priority: DefaultPriority | None = None
    default_group_id: int | None = None
    assignment_strategy: AssignmentStrategy | None = None
    fixed_assignee_id: int | None = None
    require_asset: int = 0
    sort_order: int = 0
    status: int = 1

    @field_validator("name", "code")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("字段不能为空")
        return value.strip()

    @field_validator("default_priority")
    @classmethod
    def normalize_default_priority(cls, value: str | None) -> str | None:
        return "normal" if value == "medium" else value

    @field_validator("require_asset", "status")
    @classmethod
    def validate_switch(cls, value: int) -> int:
        if value not in {0, 1}:
            raise ValueError("字段只能为 1 或 0")
        return value

    @model_validator(mode="after")
    def validate_strategy_fields(self) -> "TicketCategoryBase":
        if self.assignment_strategy == "fixed_user" and self.fixed_assignee_id is None:
            raise ValueError("fixed_user 策略必须配置 fixed_assignee_id")
        if self.assignment_strategy == "least_workload" and self.default_group_id is None:
            raise ValueError("least_workload 策略必须配置 default_group_id")
        return self


class TicketCategoryCreate(TicketCategoryBase):
    pass


class TicketCategoryUpdate(BaseModel):
    parent_id: int | None = None
    name: str | None = None
    code: str | None = None
    description: str | None = None
    default_priority: DefaultPriority | None = None
    default_group_id: int | None = None
    assignment_strategy: AssignmentStrategy | None = None
    fixed_assignee_id: int | None = None
    require_asset: int | None = None
    sort_order: int | None = None
    status: int | None = None

    @field_validator("name", "code")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("字段不能为空")
        return value.strip() if value is not None else value

    @field_validator("default_priority")
    @classmethod
    def normalize_default_priority(cls, value: str | None) -> str | None:
        return "normal" if value == "medium" else value

    @field_validator("require_asset", "status")
    @classmethod
    def validate_switch(cls, value: int | None) -> int | None:
        if value is not None and value not in {0, 1}:
            raise ValueError("字段只能为 1 或 0")
        return value


class TicketCategoryStatusUpdate(BaseModel):
    status: int

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: int) -> int:
        if value not in {0, 1}:
            raise ValueError("status 只能为 1 或 0")
        return value


class TicketCategoryRead(BaseModel):
    id: int
    parent_id: int | None = None
    name: str
    code: str
    description: str | None = None
    default_priority: str | None = None
    default_group_id: int | None = None
    default_group_name: str | None = None
    assignment_strategy: str | None = None
    fixed_assignee_id: int | None = None
    fixed_assignee_name: str | None = None
    require_asset: int
    sort_order: int
    status: int
    created_at: datetime
    updated_at: datetime


class TicketCategoryTreeNode(TicketCategoryRead):
    children: list["TicketCategoryTreeNode"] = Field(default_factory=list)


class TicketCategorySimpleOut(BaseModel):
    id: int
    name: str
    code: str
