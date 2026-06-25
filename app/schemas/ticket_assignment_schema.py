from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

AssignStrategy = Literal["least_workload", "fixed_user"]


class TicketAssignmentRuleBase(BaseModel):
    name: str
    category_id: int | None = None
    priority: str | None = None
    ops_group_id: int | None = None
    assign_strategy: AssignStrategy
    target_user_id: int | None = None
    enabled: bool = True
    sort_order: int = 100
    remark: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("规则名称不能为空")
        return value.strip()

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {"urgent", "high", "normal", "medium", "low"}
        if value not in allowed:
            raise ValueError("priority 不合法")
        return "normal" if value == "medium" else value

    @model_validator(mode="after")
    def validate_strategy_fields(self) -> "TicketAssignmentRuleBase":
        if self.assign_strategy == "least_workload" and self.ops_group_id is None:
            raise ValueError("least_workload 策略必须配置 ops_group_id")
        if self.assign_strategy == "fixed_user" and self.target_user_id is None:
            raise ValueError("fixed_user 策略必须配置 target_user_id")
        return self


class TicketAssignmentRuleCreate(TicketAssignmentRuleBase):
    pass


class TicketAssignmentRuleUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    priority: str | None = None
    ops_group_id: int | None = None
    assign_strategy: AssignStrategy | None = None
    target_user_id: int | None = None
    enabled: bool | None = None
    sort_order: int | None = None
    remark: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("规则名称不能为空")
        return value.strip() if value is not None else value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {"urgent", "high", "normal", "medium", "low"}
        if value not in allowed:
            raise ValueError("priority 不合法")
        return "normal" if value == "medium" else value


class TicketAssignmentRuleStatusUpdate(BaseModel):
    enabled: bool


class TicketAssignmentRuleRead(BaseModel):
    id: int
    name: str
    category_id: int | None = None
    priority: str | None = None
    ops_group_id: int | None = None
    ops_group_name: str | None = None
    assign_strategy: str
    target_user_id: int | None = None
    target_user_name: str | None = None
    enabled: bool
    sort_order: int
    remark: str | None = None
    created_at: datetime
    updated_at: datetime


class TicketAutoAssignRead(BaseModel):
    success: bool
    ticket_id: int
    assignee_id: int | None = None
    assignee_name: str | None = None
    rule_id: int | None = None
    assign_type: str | None = None
    assign_strategy: str | None = None
    fail_stage: str | None = None
    fail_reason: str | None = None
