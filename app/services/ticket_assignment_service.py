from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.models import (
    SysRole,
    SysUserRole,
    Ticket,
    TicketAssignmentLog,
    TicketAssignmentRule,
    TicketAssignStrategy,
    TicketAssignType,
    TicketStatus,
    User,
    WorkGroup,
    WorkGroupMember,
)
from app.schemas.ticket_assignment_schema import (
    TicketAssignmentRuleCreate,
    TicketAssignmentRuleUpdate,
)
from app.services.notification_service import NotificationService
from app.services.todo_service import TodoService
from app.utils.timezone import local_now

logger = logging.getLogger(__name__)

IT_ROLE_CODES = {"it_staff", "it_engineer"}
UNFINISHED_ASSIGNED_STATUSES = {
    TicketStatus.ASSIGNED,
    TicketStatus.PROCESSING,
    TicketStatus.PENDING_CONFIRM,
}


@dataclass
class TicketAssignmentResult:
    success: bool
    assignee: User | None = None
    rule: TicketAssignmentRule | None = None
    assign_strategy: str | None = None
    fail_stage: str | None = None
    fail_reason: str | None = None


class TicketAssignmentConflictError(Exception):
    pass


class TicketAssignmentValidationError(Exception):
    pass


class TicketAssignmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_rules(
        self,
        *,
        name: str | None = None,
        category_id: int | None = None,
        priority: str | None = None,
        ops_group_id: int | None = None,
        target_user_id: int | None = None,
        assign_strategy: str | None = None,
        enabled: bool | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[TicketAssignmentRule], int]:
        stmt = select(TicketAssignmentRule)
        if name:
            stmt = stmt.where(TicketAssignmentRule.name.like(f"%{name}%"))
        if category_id is not None:
            stmt = stmt.where(TicketAssignmentRule.category_id == category_id)
        if priority:
            stmt = stmt.where(TicketAssignmentRule.priority == priority)
        if ops_group_id is not None:
            stmt = stmt.where(TicketAssignmentRule.ops_group_id == ops_group_id)
        if target_user_id is not None:
            stmt = stmt.where(TicketAssignmentRule.target_user_id == target_user_id)
        if assign_strategy:
            stmt = stmt.where(TicketAssignmentRule.assign_strategy == assign_strategy)
        if enabled is not None:
            stmt = stmt.where(TicketAssignmentRule.enabled == int(enabled))

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(TicketAssignmentRule.sort_order.asc(), TicketAssignmentRule.id.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total

    def get_rule(self, rule_id: int) -> TicketAssignmentRule | None:
        return self.db.get(TicketAssignmentRule, rule_id)

    def create_rule(self, payload: TicketAssignmentRuleCreate) -> TicketAssignmentRule:
        data = payload.model_dump()
        self._validate_rule_data(data)
        data["enabled"] = int(data["enabled"])
        rule = TicketAssignmentRule(**data)
        self.db.add(rule)
        self.db.flush()
        return rule

    def update_rule(
        self,
        rule_id: int,
        payload: TicketAssignmentRuleUpdate,
    ) -> TicketAssignmentRule | None:
        rule = self.db.get(TicketAssignmentRule, rule_id)
        if rule is None:
            return None
        data = payload.model_dump(exclude_unset=True)
        merged = {
            "name": rule.name,
            "category_id": rule.category_id,
            "priority": rule.priority,
            "ops_group_id": rule.ops_group_id,
            "assign_strategy": str(rule.assign_strategy),
            "target_user_id": rule.target_user_id,
            "enabled": bool(rule.enabled),
            "sort_order": rule.sort_order,
            "remark": rule.remark,
        } | data
        self._validate_rule_data(merged)
        for field, value in data.items():
            setattr(rule, field, int(value) if field == "enabled" else value)
        self.db.flush()
        return rule

    def update_rule_status(
        self,
        rule_id: int,
        enabled: bool,
    ) -> TicketAssignmentRule | None:
        rule = self.db.get(TicketAssignmentRule, rule_id)
        if rule is None:
            return None
        rule.enabled = int(enabled)
        self.db.flush()
        return rule

    def delete_rule(self, rule_id: int) -> bool:
        rule = self.db.get(TicketAssignmentRule, rule_id)
        if rule is None:
            return False
        self.db.delete(rule)
        self.db.flush()
        return True

    def auto_assign_ticket(
        self,
        ticket: Ticket,
        *,
        force: bool = False,
        mutate_on_failure: bool = True,
        preserve_existing_on_failure: bool = False,
    ) -> TicketAssignmentResult:
        if ticket.handler_id is not None and not force:
            result = TicketAssignmentResult(
                success=False,
                fail_stage="apply_assignment",
                fail_reason="工单已经存在处理人，不能重复自动分配",
            )
            self.create_assignment_log(ticket, result)
            return result

        old_handler_id = ticket.handler_id
        try:
            rule = self.match_assignment_rule(ticket)
            if rule is None:
                result = TicketAssignmentResult(
                    success=False,
                    fail_stage="match_rule",
                    fail_reason="未匹配到可用自动分配规则",
                )
            elif rule.assign_strategy == TicketAssignStrategy.LEAST_WORKLOAD:
                result = self.assign_by_least_workload(ticket, rule)
            elif rule.assign_strategy == TicketAssignStrategy.FIXED_USER:
                result = self.assign_by_fixed_user(ticket, rule)
            else:
                result = TicketAssignmentResult(
                    success=False,
                    rule=rule,
                    assign_strategy=str(rule.assign_strategy),
                    fail_stage="match_rule",
                    fail_reason="不支持的自动分配策略",
                )
        except Exception:
            logger.exception("[Ticket Assignment] auto assignment failed")
            result = TicketAssignmentResult(
                success=False,
                fail_stage="unknown",
                fail_reason="自动分配执行异常",
            )

        if result.success:
            self.apply_auto_assignment(ticket, result, old_handler_id=old_handler_id)
        elif mutate_on_failure and not (
            preserve_existing_on_failure and old_handler_id is not None
        ):
            self.apply_assignment_failure(ticket)
            self.notify_auto_assignment_failed(ticket, result)

        self.create_assignment_log(ticket, result)
        self.db.flush()
        return result

    def match_assignment_rule(self, ticket: Ticket) -> TicketAssignmentRule | None:
        category_id = ticket.category_id
        priority = self._priority_value(ticket.priority)
        match_rank = case(
            (
                TicketAssignmentRule.category_id == category_id,
                case((TicketAssignmentRule.priority == priority, 0), else_=1),
            ),
            (
                TicketAssignmentRule.category_id.is_(None),
                case((TicketAssignmentRule.priority == priority, 2), else_=3),
            ),
            else_=4,
        )
        stmt = (
            select(TicketAssignmentRule)
            .where(
                TicketAssignmentRule.enabled == 1,
                or_(
                    TicketAssignmentRule.category_id == category_id,
                    TicketAssignmentRule.category_id.is_(None),
                ),
                or_(
                    TicketAssignmentRule.priority == priority,
                    TicketAssignmentRule.priority.is_(None),
                ),
            )
            .order_by(
                match_rank.asc(),
                TicketAssignmentRule.sort_order.asc(),
                TicketAssignmentRule.id.asc(),
            )
            .limit(1)
        )
        return self.db.scalar(stmt)

    def assign_by_least_workload(
        self,
        ticket: Ticket,
        rule: TicketAssignmentRule,
    ) -> TicketAssignmentResult:
        if rule.ops_group_id is None:
            return self._failure(rule, "check_group", "least_workload 策略未配置运维组")
        group = self.db.get(WorkGroup, rule.ops_group_id)
        if group is None:
            return self._failure(rule, "check_group", "匹配到规则但运维组不存在")
        if group.status != 1:
            return self._failure(rule, "check_group", "运维组已禁用")

        members = self.get_available_group_members(rule.ops_group_id)
        if not members:
            return self._failure(rule, "check_member", "运维组下没有可用成员")

        user_ids = [member.user_id for member in members]
        workloads = self.count_unfinished_tickets(user_ids)
        last_assigned = self.get_user_last_assigned_at(user_ids)
        selected_id = min(
            user_ids,
            key=lambda user_id: (
                workloads.get(user_id, 0),
                0 if last_assigned.get(user_id) is None else 1,
                last_assigned.get(user_id) or datetime.min,
                user_id,
            ),
        )
        assignee = self.db.get(User, selected_id)
        if assignee is None:
            return self._failure(rule, "select_assignee", "选择处理人失败")
        return TicketAssignmentResult(
            success=True,
            assignee=assignee,
            rule=rule,
            assign_strategy=str(rule.assign_strategy),
        )

    def assign_by_fixed_user(
        self,
        ticket: Ticket,
        rule: TicketAssignmentRule,
    ) -> TicketAssignmentResult:
        if rule.target_user_id is None:
            return self._failure(rule, "check_user", "固定处理人未配置")
        user = self.db.get(User, rule.target_user_id)
        if user is None:
            return self._failure(rule, "check_user", "固定处理人不存在")
        if user.status != 1:
            return self._failure(rule, "check_user", "固定处理人账号已禁用")
        if not self._is_it_staff(user.id):
            return self._failure(rule, "check_user", "固定处理人不是 IT 运维人员")
        if rule.ops_group_id is not None:
            member = self.db.scalar(
                select(WorkGroupMember).where(
                    WorkGroupMember.group_id == rule.ops_group_id,
                    WorkGroupMember.user_id == user.id,
                )
            )
            if member is None or member.status != 1:
                return self._failure(rule, "check_member", "固定处理人不属于指定运维组")
        return TicketAssignmentResult(
            success=True,
            assignee=user,
            rule=rule,
            assign_strategy=str(rule.assign_strategy),
        )

    def get_available_group_members(self, ops_group_id: int) -> list[WorkGroupMember]:
        members = list(
            self.db.scalars(
                select(WorkGroupMember)
                .join(User, User.id == WorkGroupMember.user_id)
                .where(
                    WorkGroupMember.group_id == ops_group_id,
                    WorkGroupMember.status == 1,
                    User.status == 1,
                )
            )
        )
        return [member for member in members if self._is_it_staff(member.user_id)]

    def count_unfinished_tickets(self, user_ids: list[int]) -> dict[int, int]:
        if not user_ids:
            return {}
        rows = self.db.execute(
            select(Ticket.handler_id, func.count(Ticket.id))
            .where(
                Ticket.handler_id.in_(user_ids),
                Ticket.status.in_(list(UNFINISHED_ASSIGNED_STATUSES)),
            )
            .group_by(Ticket.handler_id)
        ).all()
        return {int(user_id): int(count) for user_id, count in rows if user_id is not None}

    def get_user_last_assigned_at(self, user_ids: list[int]) -> dict[int, datetime | None]:
        if not user_ids:
            return {}
        rows = self.db.execute(
            select(Ticket.handler_id, func.max(Ticket.assigned_at))
            .where(Ticket.handler_id.in_(user_ids), Ticket.assigned_at.is_not(None))
            .group_by(Ticket.handler_id)
        ).all()
        return {int(user_id): assigned_at for user_id, assigned_at in rows if user_id is not None}

    def apply_auto_assignment(
        self,
        ticket: Ticket,
        result: TicketAssignmentResult,
        *,
        old_handler_id: int | None = None,
    ) -> None:
        if result.assignee is None:
            raise TicketAssignmentValidationError("自动分配结果缺少处理人")
        now = local_now()
        if old_handler_id is not None and old_handler_id != result.assignee.id:
            TodoService(self.db).cancel_business_todos(
                business_type="ticket",
                business_id=ticket.id,
                todo_type="ticket_process",
                assignee_id=old_handler_id,
                remark="工单已被重新自动分配，原待办自动取消",
            )
            NotificationService(self.db).create_notification(
                user_id=old_handler_id,
                title="工单已重新分配",
                content=f"工单 {ticket.ticket_no}/{ticket.title} 已被系统重新分配。",
                biz_type="ticket",
                biz_id=ticket.id,
            )

        ticket.handler_id = result.assignee.id
        ticket.assigner_id = None
        ticket.assign_type = TicketAssignType.AUTO
        ticket.assigned_at = now
        ticket.accepted_at = None
        ticket.status = TicketStatus.ASSIGNED
        TodoService(self.db).handle_ticket_assigned(ticket, operator_id=None)
        self.notify_auto_assignment_success(ticket, result.assignee)

    def apply_assignment_failure(self, ticket: Ticket) -> None:
        ticket.status = TicketStatus.PENDING_ACCEPT
        ticket.handler_id = None
        ticket.assigner_id = None
        ticket.assign_type = None
        ticket.assigned_at = None
        ticket.accepted_at = None

    def create_assignment_log(
        self,
        ticket: Ticket,
        result: TicketAssignmentResult,
    ) -> TicketAssignmentLog:
        log = TicketAssignmentLog(
            ticket_id=ticket.id,
            rule_id=result.rule.id if result.rule else None,
            ops_group_id=result.rule.ops_group_id if result.rule else None,
            assignee_id=result.assignee.id if result.assignee else None,
            assign_type=TicketAssignType.AUTO if result.success else None,
            assign_strategy=result.assign_strategy,
            success=1 if result.success else 0,
            fail_stage=result.fail_stage,
            fail_reason=result.fail_reason,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def notify_auto_assignment_success(self, ticket: Ticket, assignee: User) -> None:
        NotificationService(self.db).create_notification(
            user_id=assignee.id,
            title="新的工单分配",
            content=f"系统已自动将工单 {ticket.ticket_no}/{ticket.title} 分配给你，请及时处理。",
            biz_type="ticket",
            biz_id=ticket.id,
        )

    def notify_auto_assignment_failed(
        self,
        ticket: Ticket,
        result: TicketAssignmentResult,
    ) -> None:
        TodoService(self.db).create_ticket_assign_todos(ticket, created_by=ticket.reporter_id)
        logger.info(
            "[Ticket Assignment] ticket=%s auto assign failed: %s",
            ticket.id,
            result.fail_reason,
        )

    def result_dict(self, ticket: Ticket, result: TicketAssignmentResult) -> dict:
        assignee = result.assignee
        return {
            "success": result.success,
            "ticket_id": ticket.id,
            "assignee_id": assignee.id if assignee else None,
            "assignee_name": assignee.real_name if assignee else None,
            "rule_id": result.rule.id if result.rule else None,
            "assign_type": TicketAssignType.AUTO if result.success else None,
            "assign_strategy": result.assign_strategy,
            "fail_stage": result.fail_stage,
            "fail_reason": result.fail_reason,
        }

    def _validate_rule_data(self, data: dict) -> None:
        strategy = data.get("assign_strategy")
        if strategy not in {TicketAssignStrategy.LEAST_WORKLOAD, TicketAssignStrategy.FIXED_USER}:
            raise TicketAssignmentValidationError("assign_strategy 不合法")
        ops_group_id = data.get("ops_group_id")
        target_user_id = data.get("target_user_id")
        if strategy == TicketAssignStrategy.LEAST_WORKLOAD:
            if ops_group_id is None:
                raise TicketAssignmentValidationError("least_workload 策略必须配置 ops_group_id")
            group = self.db.get(WorkGroup, ops_group_id)
            if group is None or group.status != 1:
                raise TicketAssignmentValidationError("运维组不存在或未启用")
        if strategy == TicketAssignStrategy.FIXED_USER:
            if target_user_id is None:
                raise TicketAssignmentValidationError("fixed_user 策略必须配置 target_user_id")
            user = self.db.get(User, target_user_id)
            if user is None or user.status != 1:
                raise TicketAssignmentValidationError("固定处理人不存在或未启用")
            if not self._is_it_staff(target_user_id):
                raise TicketAssignmentValidationError("固定处理人不是 IT 运维人员")
            if ops_group_id is not None:
                group = self.db.get(WorkGroup, ops_group_id)
                if group is None or group.status != 1:
                    raise TicketAssignmentValidationError("运维组不存在或未启用")
                member = self.db.scalar(
                    select(WorkGroupMember).where(
                        WorkGroupMember.group_id == ops_group_id,
                        WorkGroupMember.user_id == target_user_id,
                        WorkGroupMember.status == 1,
                    )
                )
                if member is None:
                    raise TicketAssignmentValidationError("固定处理人不属于指定运维组")

    def _is_it_staff(self, user_id: int) -> bool:
        return (
            self.db.scalar(
                select(func.count())
                .select_from(SysUserRole)
                .join(SysRole, SysRole.id == SysUserRole.role_id)
                .where(
                    SysUserRole.user_id == user_id,
                    SysRole.status == 1,
                    SysRole.role_code.in_(IT_ROLE_CODES),
                )
            )
            or 0
        ) > 0

    def _failure(
        self,
        rule: TicketAssignmentRule,
        stage: str,
        reason: str,
    ) -> TicketAssignmentResult:
        return TicketAssignmentResult(
            success=False,
            rule=rule,
            assign_strategy=str(rule.assign_strategy),
            fail_stage=stage,
            fail_reason=reason,
        )

    def _priority_value(self, priority: object) -> str | None:
        if priority is None:
            return None
        value = getattr(priority, "value", str(priority))
        return "normal" if value == "medium" else value
