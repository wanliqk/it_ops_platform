from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import SlaRule
from app.schemas.sla_rule_schema import SlaRuleCreate, SlaRuleUpdate

DEFAULT_RESPONSE_MINUTES = 60
DEFAULT_RESOLVE_MINUTES = 480
PRIORITY_NORMALIZATION = {"normal": "medium"}


class SlaService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_rules(
        self,
        *,
        priority: str | None = None,
        ticket_category: str | None = None,
        enabled: int | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[SlaRule], int]:
        stmt = select(SlaRule)
        if priority:
            stmt = stmt.where(SlaRule.priority == self.normalize_priority(priority))
        if ticket_category is not None:
            stmt = stmt.where(SlaRule.ticket_category == ticket_category)
        if enabled is not None:
            stmt = stmt.where(SlaRule.enabled == enabled)

        total = len(list(self.db.scalars(stmt)))
        items = list(
            self.db.scalars(
                stmt.order_by(SlaRule.sort_order.asc(), SlaRule.id.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total

    def get_rule(self, rule_id: int) -> SlaRule | None:
        return self.db.get(SlaRule, rule_id)

    def create_rule(self, payload: SlaRuleCreate) -> SlaRule:
        rule = SlaRule(**payload.model_dump())
        rule.priority = self.normalize_priority(rule.priority)
        self.db.add(rule)
        self.db.flush()
        return rule

    def update_rule(self, rule_id: int, payload: SlaRuleUpdate) -> SlaRule | None:
        rule = self.get_rule(rule_id)
        if rule is None:
            return None

        data = payload.model_dump(exclude_unset=True)
        if "priority" in data and data["priority"] is not None:
            data["priority"] = self.normalize_priority(data["priority"])

        response_minutes = data.get("response_minutes", rule.response_minutes)
        resolve_minutes = data.get("resolve_minutes", rule.resolve_minutes)
        if resolve_minutes < response_minutes:
            raise ValueError("resolve_minutes 必须大于或等于 response_minutes")

        for field, value in data.items():
            setattr(rule, field, value)
        self.db.flush()
        return rule

    def update_enabled(self, rule_id: int, enabled: int) -> SlaRule | None:
        rule = self.get_rule(rule_id)
        if rule is None:
            return None
        rule.enabled = enabled
        self.db.flush()
        return rule

    def delete_rule(self, rule_id: int) -> bool:
        rule = self.get_rule(rule_id)
        if rule is None:
            return False
        self.db.delete(rule)
        self.db.flush()
        return True

    def match_rule(self, ticket_category: str | None, priority: str) -> SlaRule | None:
        normalized_priority = self.normalize_priority(priority)
        stmt = (
            select(SlaRule)
            .where(
                SlaRule.enabled == 1,
                SlaRule.priority == normalized_priority,
                or_(SlaRule.ticket_category == ticket_category, SlaRule.ticket_category.is_(None)),
            )
            .order_by(
                (SlaRule.ticket_category.is_(None)).asc(),
                SlaRule.sort_order.asc(),
                SlaRule.id.asc(),
            )
            .limit(1)
        )
        return self.db.scalar(stmt)

    def calculate_ticket_sla_deadline(
        self,
        *,
        created_at: datetime,
        ticket_category: str | None,
        priority: str,
    ) -> tuple[datetime, datetime]:
        rule = self.match_rule(ticket_category, priority)
        response_minutes = rule.response_minutes if rule else DEFAULT_RESPONSE_MINUTES
        resolve_minutes = rule.resolve_minutes if rule else DEFAULT_RESOLVE_MINUTES
        return (
            created_at + timedelta(minutes=response_minutes),
            created_at + timedelta(minutes=resolve_minutes),
        )

    def normalize_priority(self, priority: str) -> str:
        return PRIORITY_NORMALIZATION.get(priority, priority)


def calculate_ticket_sla_deadline(
    db: Session,
    *,
    created_at: datetime,
    ticket_category: str | None,
    priority: str,
) -> tuple[datetime, datetime]:
    return SlaService(db).calculate_ticket_sla_deadline(
        created_at=created_at,
        ticket_category=ticket_category,
        priority=priority,
    )
