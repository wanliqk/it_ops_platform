from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.models import (
    Asset,
    AssetStatus,
    RepairRecord,
    RepairResult,
    Ticket,
    TicketAction,
    TicketRecord,
    TicketStatus,
    User,
)
from app.schemas.ticket import (
    TicketAssign,
    TicketCancel,
    TicketComplete,
    TicketCreate,
    TicketStart,
    TicketUpdate,
)
from app.services.sla_service import SlaService
from app.services.ticket_assignment_service import TicketAssignmentService
from app.services.todo_service import TodoService
from app.utils.permissions import get_user_permission_codes, get_user_role_codes
from app.utils.timezone import local_now


class TicketConflictError(Exception):
    pass


class TicketService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: TicketCreate) -> Ticket:
        data = payload.model_dump()
        data["ticket_no"] = data["ticket_no"] or self._generate_ticket_no()
        created_at = local_now()
        data["created_at"] = created_at
        sla_response_deadline, sla_resolve_deadline = SlaService(
            self.db
        ).calculate_ticket_sla_deadline(
            created_at=created_at,
            ticket_category=self._enum_value(data.get("fault_type")),
            priority=self._enum_value(data.get("priority")) or "normal",
        )
        data["sla_response_deadline"] = sla_response_deadline
        data["sla_resolve_deadline"] = sla_resolve_deadline
        ticket = Ticket(**data)
        self.db.add(ticket)
        self.db.flush()
        assignment_result = TicketAssignmentService(self.db).auto_assign_ticket(ticket)
        self.db.add(
            TicketRecord(
                ticket_id=ticket.id,
                operator_id=ticket.reporter_id,
                from_status=None,
                to_status=ticket.status,
                action=TicketAction.CREATE,
                remark=(
                    "用户提交报修工单，系统自动分配成功"
                    if assignment_result.success
                    else f"用户提交报修工单，自动分配失败：{assignment_result.fail_reason}"
                ),
            )
        )
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def get(self, ticket_id: int) -> Ticket | None:
        return self.db.get(Ticket, ticket_id)

    def list(
        self,
        *,
        current_user: User,
        keyword: str | None = None,
        status: str | None = None,
        fault_type: str | None = None,
        priority: str | None = None,
        reporter_id: int | None = None,
        handler_id: int | None = None,
        asset_id: int | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Ticket], int]:
        stmt = select(Ticket)
        permission_codes = get_user_permission_codes(self.db, current_user.id)
        if "ticket:view_all" not in permission_codes:
            stmt = stmt.where(Ticket.reporter_id == current_user.id)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(Ticket.ticket_no.like(like), Ticket.title.like(like)))
        if status:
            stmt = stmt.where(Ticket.status == status)
        if fault_type:
            stmt = stmt.where(Ticket.fault_type == fault_type)
        if priority:
            stmt = stmt.where(Ticket.priority == priority)
        if reporter_id is not None:
            stmt = stmt.where(Ticket.reporter_id == reporter_id)
        if handler_id is not None:
            stmt = stmt.where(Ticket.handler_id == handler_id)
        if asset_id is not None:
            stmt = stmt.where(Ticket.asset_id == asset_id)

        total = len(list(self.db.scalars(stmt)))
        items = list(
            self.db.scalars(
                stmt.order_by(Ticket.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total

    def update(self, ticket_id: int, payload: TicketUpdate) -> Ticket | None:
        ticket = self.db.get(Ticket, ticket_id)
        if ticket is None:
            return None

        before_status = ticket.status
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(ticket, field, value)

        if payload.status is not None and payload.status != before_status:
            self._apply_sla_flow_timestamps(ticket, payload.status, local_now())
            self.db.add(
                TicketRecord(
                    ticket_id=ticket.id,
                    operator_id=payload.handler_id or ticket.handler_id or ticket.reporter_id,
                    from_status=before_status,
                    to_status=payload.status,
                    action=self._action_for_status(payload.status),
                    remark="工单状态变更",
                )
            )

        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def assign(self, ticket_id: int, payload: TicketAssign, operator_id: int) -> Ticket | None:
        ticket = self.get(ticket_id)
        if ticket is None:
            return None
        if ticket.status not in {TicketStatus.PENDING, TicketStatus.PENDING_ACCEPT}:
            raise TicketConflictError
        before_status = ticket.status
        ticket.handler_id = payload.handler_id
        ticket.assigner_id = operator_id
        ticket.assign_type = "manual"
        ticket.status = TicketStatus.ASSIGNED
        now = local_now()
        ticket.assigned_at = now
        ticket.accepted_at = None
        self._apply_sla_flow_timestamps(ticket, TicketStatus.ASSIGNED, now)
        self._add_record(
            ticket,
            operator_id,
            before_status,
            TicketStatus.ASSIGNED,
            TicketAction.ASSIGN,
            payload.remark,
        )
        TodoService(self.db).handle_ticket_assigned(ticket, operator_id=operator_id)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def start(self, ticket_id: int, payload: TicketStart, operator: User) -> Ticket | None:
        ticket = self.get(ticket_id)
        if ticket is None:
            return None
        self._ensure_status(ticket.status, TicketStatus.ASSIGNED)
        if not self._is_admin(operator) and ticket.handler_id not in {None, operator.id}:
            raise PermissionError
        if ticket.handler_id is None:
            ticket.handler_id = operator.id
            ticket.assign_type = "claim"
        ticket.status = TicketStatus.PROCESSING
        now = local_now()
        ticket.accepted_at = now
        ticket.started_at = now
        self._apply_sla_flow_timestamps(ticket, TicketStatus.PROCESSING, now)
        self._add_record(
            ticket,
            operator.id,
            TicketStatus.ASSIGNED,
            TicketStatus.PROCESSING,
            TicketAction.START,
            payload.remark,
        )
        TodoService(self.db).handle_ticket_started(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def complete(self, ticket_id: int, payload: TicketComplete, operator: User) -> Ticket | None:
        ticket = self.get(ticket_id)
        if ticket is None:
            return None
        self._ensure_status(ticket.status, TicketStatus.PROCESSING)
        if not self._is_admin(operator) and ticket.handler_id != operator.id:
            raise PermissionError
        now = local_now()
        ticket.status = TicketStatus.COMPLETED
        ticket.result = payload.result
        ticket.completed_at = now
        ticket.resolved_at = now
        if ticket.asset_id is not None:
            repair_user_id = ticket.handler_id or operator.id
            self.db.add(
                RepairRecord(
                    ticket_id=ticket.id,
                    asset_id=ticket.asset_id,
                    repair_user_id=repair_user_id,
                    fault_reason=payload.fault_reason,
                    repair_method=payload.repair_method,
                    repair_result=payload.repair_result,
                    repair_cost=payload.repair_cost,
                    repaired_at=now,
                )
            )
            asset = self.db.get(Asset, ticket.asset_id)
            if asset is not None:
                asset.status = self._asset_status_after_repair(payload)
        self._add_record(
            ticket,
            operator.id,
            TicketStatus.PROCESSING,
            TicketStatus.COMPLETED,
            TicketAction.FINISH,
            payload.remark,
        )
        TodoService(self.db).handle_ticket_completed(ticket, operator_id=operator.id)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def cancel(self, ticket_id: int, payload: TicketCancel, operator: User) -> Ticket | None:
        ticket = self.get(ticket_id)
        if ticket is None:
            return None
        if self._is_admin(operator):
            if ticket.status not in {TicketStatus.PENDING, TicketStatus.ASSIGNED}:
                raise TicketConflictError
        elif ticket.reporter_id == operator.id:
            self._ensure_status(ticket.status, TicketStatus.PENDING)
        else:
            raise PermissionError
        before_status = ticket.status
        ticket.status = TicketStatus.CANCELLED
        self._add_record(
            ticket,
            operator.id,
            before_status,
            TicketStatus.CANCELLED,
            TicketAction.CANCEL,
            payload.reason,
        )
        TodoService(self.db).handle_ticket_cancelled(ticket, remark=payload.reason)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def records(self, ticket_id: int) -> list[TicketRecord]:
        return list(
            self.db.scalars(
                select(TicketRecord)
                .where(TicketRecord.ticket_id == ticket_id)
                .order_by(TicketRecord.created_at.asc())
            )
        )

    def delete(self, ticket_id: int) -> bool:
        ticket = self.get(ticket_id)
        if ticket is None:
            return False
        if ticket.status not in {TicketStatus.PENDING, TicketStatus.CANCELLED}:
            raise TicketConflictError
        has_repair = self.db.scalar(
            select(RepairRecord.id).where(RepairRecord.ticket_id == ticket_id).limit(1)
        )
        if has_repair is not None:
            raise TicketConflictError
        self.db.execute(delete(TicketRecord).where(TicketRecord.ticket_id == ticket_id))
        self.db.delete(ticket)
        self.db.commit()
        return True

    def can_access(self, ticket: Ticket, user: User) -> bool:
        permission_codes = get_user_permission_codes(self.db, user.id)
        return "ticket:view_all" in permission_codes or (
            "ticket:view_self" in permission_codes and ticket.reporter_id == user.id
        )

    def can_update(self, ticket: Ticket, user: User) -> bool:
        if self._is_admin(user):
            return True
        return ticket.reporter_id == user.id and ticket.status == TicketStatus.PENDING

    def _is_admin(self, user: User) -> bool:
        return "admin" in get_user_role_codes(self.db, user.id)

    def _generate_ticket_no(self) -> str:
        today = local_now().strftime("%Y%m%d")
        prefix = f"TK{today}"
        latest_no = self.db.scalar(
            select(func.max(Ticket.ticket_no)).where(Ticket.ticket_no.like(f"{prefix}%"))
        )
        if latest_no:
            sequence = int(latest_no[-4:]) + 1
        else:
            sequence = 1
        return f"{prefix}{sequence:04d}"

    def _action_for_status(self, status: TicketStatus) -> TicketAction:
        actions = {
            TicketStatus.ASSIGNED: TicketAction.ASSIGN,
            TicketStatus.PROCESSING: TicketAction.START,
            TicketStatus.COMPLETED: TicketAction.FINISH,
            TicketStatus.CANCELLED: TicketAction.CANCEL,
        }
        return actions.get(status, TicketAction.CREATE)

    def _ensure_status(self, current: TicketStatus, expected: TicketStatus) -> None:
        if current != expected:
            raise TicketConflictError

    def _apply_sla_flow_timestamps(
        self,
        ticket: Ticket,
        status: TicketStatus,
        now: datetime,
    ) -> None:
        if (
            status in {TicketStatus.ASSIGNED, TicketStatus.PROCESSING}
            and ticket.first_response_at is None
        ):
            ticket.first_response_at = now
        if status == TicketStatus.COMPLETED:
            ticket.resolved_at = now

    def _enum_value(self, value: object) -> str | None:
        if value is None:
            return None
        return getattr(value, "value", str(value))

    def _add_record(
        self,
        ticket: Ticket,
        operator_id: int,
        from_status: TicketStatus | None,
        to_status: TicketStatus,
        action: TicketAction,
        remark: str | None,
    ) -> None:
        self.db.add(
            TicketRecord(
                ticket_id=ticket.id,
                operator_id=operator_id,
                from_status=from_status,
                to_status=to_status,
                action=action,
                remark=remark,
            )
        )

    def _asset_status_after_repair(self, payload: TicketComplete) -> AssetStatus:
        if payload.asset_status_after_repair:
            return AssetStatus(payload.asset_status_after_repair)
        if payload.repair_result in {RepairResult.FIXED, RepairResult.REPLACE_REPAIR}:
            return AssetStatus.IN_USE
        if payload.repair_result == RepairResult.SCRAPPED:
            return AssetStatus.SCRAPPED
        return AssetStatus.REPAIRING
