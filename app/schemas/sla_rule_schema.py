from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

SlaPriority = Literal["urgent", "high", "medium", "low"]


class SlaRuleBase(BaseModel):
    name: str
    category_id: int | None = None
    priority: SlaPriority
    response_minutes: int
    resolve_minutes: int
    enabled: int = 1
    sort_order: int = 0

    @field_validator("response_minutes", "resolve_minutes")
    @classmethod
    def validate_positive_minutes(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("时限必须大于 0")
        return value

    @field_validator("enabled")
    @classmethod
    def validate_enabled(cls, value: int) -> int:
        if value not in {0, 1}:
            raise ValueError("enabled 只能为 1 或 0")
        return value

    @model_validator(mode="after")
    def validate_resolve_not_less_than_response(self) -> "SlaRuleBase":
        if self.resolve_minutes < self.response_minutes:
            raise ValueError("resolve_minutes 必须大于或等于 response_minutes")
        return self


class SlaRuleCreate(SlaRuleBase):
    pass


class SlaRuleUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    priority: SlaPriority | None = None
    response_minutes: int | None = None
    resolve_minutes: int | None = None
    enabled: int | None = None
    sort_order: int | None = None

    @field_validator("response_minutes", "resolve_minutes")
    @classmethod
    def validate_positive_minutes(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("时限必须大于 0")
        return value

    @field_validator("enabled")
    @classmethod
    def validate_enabled(cls, value: int | None) -> int | None:
        if value is not None and value not in {0, 1}:
            raise ValueError("enabled 只能为 1 或 0")
        return value

    @model_validator(mode="after")
    def validate_resolve_not_less_than_response(self) -> "SlaRuleUpdate":
        if (
            self.response_minutes is not None
            and self.resolve_minutes is not None
            and self.resolve_minutes < self.response_minutes
        ):
            raise ValueError("resolve_minutes 必须大于或等于 response_minutes")
        return self


class SlaRuleEnabledUpdate(BaseModel):
    enabled: int

    @field_validator("enabled")
    @classmethod
    def validate_enabled(cls, value: int) -> int:
        if value not in {0, 1}:
            raise ValueError("enabled 只能为 1 或 0")
        return value


class SlaRuleRead(SlaRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
