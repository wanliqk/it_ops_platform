from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import SlaRule, Ticket, TicketStatus
from app.schemas.sla_rule_schema import SlaRuleCreate, SlaRuleUpdate
from app.services.notification_service import NotificationService
from app.utils.timezone import local_now

DEFAULT_RESPONSE_MINUTES = 60
DEFAULT_RESOLVE_MINUTES = 480
PRIORITY_NORMALIZATION = {"normal": "medium"}
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SlaTimeoutCheckResult:
    scanned: int
    response_overdue: int
    resolve_overdue: int
    notification_created: int
    skipped: int


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

    def check_ticket_sla_timeout(self) -> SlaTimeoutCheckResult:
        logger.info("[SLA Timeout] start checking")
        now = local_now()
        tickets = list(
            self.db.scalars(
                select(Ticket)
                .where(
                    Ticket.status.notin_(
                        [TicketStatus.COMPLETED, TicketStatus.CLOSED, TicketStatus.CANCELLED]
                    ),
                    or_(
                        and_(
                            Ticket.response_overdue == 0,
                            Ticket.first_response_at.is_(None),
                            Ticket.sla_response_deadline.is_not(None),
                            Ticket.sla_response_deadline < now,
                        ),
                        and_(
                            Ticket.resolve_overdue == 0,
                            Ticket.resolved_at.is_(None),
                            Ticket.sla_resolve_deadline.is_not(None),
                            Ticket.sla_resolve_deadline < now,
                        ),
                    ),
                )
            )
        )
        notification_service = NotificationService(self.db)
        response_overdue_count = 0
        resolve_overdue_count = 0
        notification_created_count = 0
        skipped_count = 0

        for ticket in tickets:
            if (
                ticket.sla_response_deadline is not None
                and ticket.first_response_at is None
                and ticket.response_overdue == 0
                and self._is_past_deadline(ticket.sla_response_deadline, now)
            ):
                ticket.response_overdue = 1
                response_overdue_count += 1
                notification_created = self._create_timeout_notification(
                    notification_service,
                    ticket=ticket,
                    title="工单响应已超时",
                    content=(
                        f"工单 {ticket.ticket_no}/{ticket.title} "
                        "已超过 SLA 响应时间，请尽快处理。"
                    ),
                )
                if notification_created:
                    notification_created_count += 1
                else:
                    skipped_count += 1
                logger.info("[SLA Timeout] ticket %s response overdue", ticket.id)

            if (
                ticket.sla_resolve_deadline is not None
                and ticket.resolved_at is None
                and ticket.resolve_overdue == 0
                and self._is_past_deadline(ticket.sla_resolve_deadline, now)
            ):
                ticket.resolve_overdue = 1
                resolve_overdue_count += 1
                notification_created = self._create_timeout_notification(
                    notification_service,
                    ticket=ticket,
                    title="工单处理已超时",
                    content=(
                        f"工单 {ticket.ticket_no}/{ticket.title} "
                        "已超过 SLA 处理完成时间，请尽快处理。"
                    ),
                )
                if notification_created:
                    notification_created_count += 1
                else:
                    skipped_count += 1
                logger.info("[SLA Timeout] ticket %s resolve overdue", ticket.id)

        self.db.flush()
        result = SlaTimeoutCheckResult(
            scanned=len(tickets),
            response_overdue=response_overdue_count,
            resolve_overdue=resolve_overdue_count,
            notification_created=notification_created_count,
            skipped=skipped_count,
        )
        logger.info(
            "[SLA Timeout] scanned=%s response_overdue=%s "
            "resolve_overdue=%s notification_created=%s skipped=%s",
            result.scanned,
            result.response_overdue,
            result.resolve_overdue,
            result.notification_created,
            result.skipped,
        )
        logger.info("[SLA Timeout] finished")
        return result

    def _is_past_deadline(
        self,
        deadline: datetime,
        now: datetime,
    ) -> bool:
        if deadline.tzinfo is None:
            return now > deadline
        return datetime.now(deadline.tzinfo) > deadline

    def _create_timeout_notification(
        self,
        notification_service: NotificationService,
        *,
        ticket: Ticket,
        title: str,
        content: str,
    ) -> bool:
        recipient_id = ticket.handler_id or ticket.reporter_id
        if recipient_id is None:
            logger.warning("跳过 SLA 超时通知，工单 %s 没有可通知用户", ticket.id)
            return False
        notification_service.create_notification(
            user_id=recipient_id,
            title=title,
            content=content,
            biz_type="ticket",
            biz_id=ticket.id,
        )
        return True


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


def check_ticket_sla_timeout(db: Session) -> SlaTimeoutCheckResult:
    return SlaService(db).check_ticket_sla_timeout()
