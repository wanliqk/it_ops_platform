from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, time

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import SysRole, SysUserRole, Ticket, Todo, TodoStatus, User
from app.schemas.todo_schema import TodoCreate
from app.services.notification_service import NotificationService
from app.utils.permissions import get_user_role_codes
from app.utils.timezone import local_now

logger = logging.getLogger(__name__)
ACTIVE_TODO_STATUSES = {TodoStatus.PENDING, TodoStatus.PROCESSING, TodoStatus.EXPIRED}


class TodoConflictError(Exception):
    pass


@dataclass(frozen=True)
class TodoTimeoutCheckResult:
    scanned: int
    expired: int
    notification_created: int
    skipped: int


class TodoService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_my(
        self,
        *,
        user_id: int,
        status: str | None = None,
        todo_type: str | None = None,
        business_type: str | None = None,
        priority: str | None = None,
        keyword: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Todo], int]:
        return self._list(
            assignee_id=user_id,
            status=status,
            todo_type=todo_type,
            business_type=business_type,
            priority=priority,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )

    def list_all(
        self,
        *,
        assignee_id: int | None = None,
        status: str | None = None,
        todo_type: str | None = None,
        business_type: str | None = None,
        priority: str | None = None,
        keyword: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Todo], int]:
        return self._list(
            assignee_id=assignee_id,
            status=status,
            todo_type=todo_type,
            business_type=business_type,
            priority=priority,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )

    def get(self, todo_id: int) -> Todo | None:
        todo = self.db.scalar(select(Todo).where(Todo.id == todo_id, Todo.is_deleted == 0))
        if todo is not None:
            self._attach_business_info([todo])
        return todo

    def can_access(self, todo: Todo, user: User) -> bool:
        return todo.assignee_id == user.id or "admin" in get_user_role_codes(self.db, user.id)

    def create(self, payload: TodoCreate) -> Todo:
        assignee = self.db.get(User, payload.assignee_id)
        todo = self.create_for_business(
            title=payload.title,
            content=payload.content,
            todo_type=payload.todo_type,
            business_type=payload.business_type,
            business_id=payload.business_id,
            assignee_id=payload.assignee_id,
            assignee_name=assignee.real_name if assignee else None,
            priority=payload.priority,
            deadline_at=payload.deadline_at,
            remark=payload.remark,
            created_by=payload.created_by,
            notify=True,
        )
        return todo

    def start(self, todo_id: int, user: User, remark: str | None = None) -> Todo | None:
        todo = self.get(todo_id)
        if todo is None:
            return None
        if not self.can_access(todo, user):
            raise PermissionError
        if todo.status != TodoStatus.PENDING:
            raise TodoConflictError
        todo.status = TodoStatus.PROCESSING
        if remark:
            todo.remark = remark
        self.db.flush()
        return todo

    def complete(self, todo_id: int, user: User, remark: str | None = None) -> Todo | None:
        todo = self.get(todo_id)
        if todo is None:
            return None
        if not self.can_access(todo, user):
            raise PermissionError
        if todo.status not in ACTIVE_TODO_STATUSES:
            raise TodoConflictError
        todo.status = TodoStatus.COMPLETED
        todo.completed_at = local_now()
        if remark:
            todo.remark = remark
        self.db.flush()
        return todo

    def cancel(
        self,
        todo_id: int,
        user: User | None = None,
        remark: str | None = None,
    ) -> Todo | None:
        todo = self.get(todo_id)
        if todo is None:
            return None
        if user is not None and not self.can_access(todo, user):
            raise PermissionError
        if todo.status not in ACTIVE_TODO_STATUSES:
            raise TodoConflictError
        self._cancel_todo(todo, remark=remark)
        self.db.flush()
        return todo

    def statistics(self, user_id: int) -> dict[str, int]:
        today_start = datetime.combine(local_now().date(), time.min)
        today_end = datetime.combine(local_now().date(), time.max)
        base = select(Todo).where(Todo.assignee_id == user_id, Todo.is_deleted == 0)
        return {
            "pending_count": self._count(base.where(Todo.status == TodoStatus.PENDING)),
            "processing_count": self._count(base.where(Todo.status == TodoStatus.PROCESSING)),
            "expired_count": self._count(base.where(Todo.status == TodoStatus.EXPIRED)),
            "today_deadline_count": self._count(
                base.where(
                    Todo.status.in_([TodoStatus.PENDING, TodoStatus.PROCESSING]),
                    Todo.deadline_at >= today_start,
                    Todo.deadline_at <= today_end,
                )
            ),
            "urgent_count": self._count(
                base.where(
                    Todo.status.in_([TodoStatus.PENDING, TodoStatus.PROCESSING]),
                    Todo.priority == "urgent",
                )
            ),
        }

    def create_ticket_assign_todos(self, ticket: Ticket, *, created_by: int | None = None) -> None:
        for admin in self._admin_users():
            self.create_for_business(
                title=f"待派单：{ticket.title}",
                content=f"工单 {ticket.ticket_no}/{ticket.title} 待派单，请及时处理。",
                todo_type="ticket_assign",
                business_type="ticket",
                business_id=ticket.id,
                assignee_id=admin.id,
                assignee_name=admin.real_name,
                priority=str(ticket.priority),
                deadline_at=ticket.sla_response_deadline,
                created_by=created_by or ticket.reporter_id,
                notify=True,
            )

    def handle_ticket_assigned(self, ticket: Ticket, *, operator_id: int | None = None) -> None:
        self.cancel_business_todos(
            business_type="ticket",
            business_id=ticket.id,
            todo_type="ticket_assign",
            remark="工单已派单，待办自动取消",
        )
        if ticket.handler_id is None:
            return
        handler = self.db.get(User, ticket.handler_id)
        self.create_for_business(
            title=f"待处理工单：{ticket.title}",
            content=f"工单 {ticket.ticket_no}/{ticket.title} 已分配给你，请及时处理。",
            todo_type="ticket_process",
            business_type="ticket",
            business_id=ticket.id,
            assignee_id=ticket.handler_id,
            assignee_name=handler.real_name if handler else None,
            priority=str(ticket.priority),
            deadline_at=ticket.sla_resolve_deadline,
            created_by=operator_id,
            notify=True,
        )

    def handle_ticket_started(self, ticket: Ticket) -> None:
        for todo in self._active_business_todos(
            business_type="ticket",
            business_id=ticket.id,
            todo_type="ticket_process",
            assignee_id=ticket.handler_id,
        ):
            if todo.status == TodoStatus.PENDING:
                todo.status = TodoStatus.PROCESSING
        self.db.flush()

    def handle_ticket_completed(self, ticket: Ticket, *, operator_id: int | None = None) -> None:
        self.complete_business_todos(
            business_type="ticket",
            business_id=ticket.id,
            todo_type="ticket_process",
            assignee_id=ticket.handler_id,
            remark="工单已处理完成，待办自动完成",
        )
        reporter = self.db.get(User, ticket.reporter_id)
        self.create_for_business(
            title=f"待确认工单：{ticket.title}",
            content=f"工单 {ticket.ticket_no}/{ticket.title} 已处理完成，请确认结果。",
            todo_type="ticket_confirm",
            business_type="ticket",
            business_id=ticket.id,
            assignee_id=ticket.reporter_id,
            assignee_name=reporter.real_name if reporter else None,
            priority=str(ticket.priority),
            deadline_at=None,
            created_by=operator_id,
            notify=True,
        )

    def handle_ticket_cancelled(self, ticket: Ticket, remark: str | None = None) -> None:
        self.cancel_business_todos(
            business_type="ticket",
            business_id=ticket.id,
            remark=remark or "工单已取消，待办自动取消",
        )

    def cancel_business_todos(
        self,
        *,
        business_type: str,
        business_id: int,
        todo_type: str | None = None,
        assignee_id: int | None = None,
        remark: str | None = None,
    ) -> int:
        todos = self._active_business_todos(
            business_type=business_type,
            business_id=business_id,
            todo_type=todo_type,
            assignee_id=assignee_id,
        )
        for todo in todos:
            self._cancel_todo(todo, remark=remark)
        self.db.flush()
        return len(todos)

    def complete_business_todos(
        self,
        *,
        business_type: str,
        business_id: int,
        todo_type: str | None = None,
        assignee_id: int | None = None,
        remark: str | None = None,
    ) -> int:
        todos = self._active_business_todos(
            business_type=business_type,
            business_id=business_id,
            todo_type=todo_type,
            assignee_id=assignee_id,
        )
        now = local_now()
        for todo in todos:
            todo.status = TodoStatus.COMPLETED
            todo.completed_at = now
            if remark:
                todo.remark = remark
        self.db.flush()
        return len(todos)

    def create_for_business(
        self,
        *,
        title: str,
        content: str,
        todo_type: str,
        business_type: str,
        business_id: int,
        assignee_id: int,
        assignee_name: str | None = None,
        priority: str = "normal",
        deadline_at: datetime | None = None,
        remark: str | None = None,
        created_by: int | None = None,
        notify: bool = False,
    ) -> Todo:
        existing = self.db.scalar(
            select(Todo).where(
                Todo.business_type == business_type,
                Todo.business_id == business_id,
                Todo.todo_type == todo_type,
                Todo.assignee_id == assignee_id,
                Todo.status.in_(list(ACTIVE_TODO_STATUSES)),
                Todo.is_deleted == 0,
            )
        )
        if existing is not None:
            return existing

        todo = Todo(
            todo_no=self._generate_todo_no(),
            title=title,
            content=content,
            todo_type=todo_type,
            business_type=business_type,
            business_id=business_id,
            assignee_id=assignee_id,
            assignee_name=assignee_name,
            status=TodoStatus.PENDING,
            priority=priority,
            deadline_at=deadline_at,
            remark=remark,
            created_by=created_by,
        )
        self.db.add(todo)
        self.db.flush()
        if notify:
            NotificationService(self.db).create_notification(
                user_id=assignee_id,
                title="你有一个新的待办事项",
                content=title,
                biz_type=business_type,
                biz_id=business_id,
            )
        return todo

    def check_todo_timeout(self) -> TodoTimeoutCheckResult:
        logger.info("[Todo Timeout] start checking")
        now = local_now()
        todos = list(
            self.db.scalars(
                select(Todo).where(
                    Todo.is_deleted == 0,
                    Todo.status.in_([TodoStatus.PENDING, TodoStatus.PROCESSING]),
                    Todo.deadline_at.is_not(None),
                    Todo.deadline_at < now,
                    Todo.expire_notice_sent == 0,
                )
            )
        )
        expired_count = 0
        notification_created = 0
        skipped = 0
        notification_service = NotificationService(self.db)
        for todo in todos:
            todo.status = TodoStatus.EXPIRED
            todo.expire_notice_sent = 1
            todo.reminded_at = now
            expired_count += 1
            if todo.assignee_id is None:
                skipped += 1
                logger.warning("跳过待办超时通知，待办 %s 没有处理人", todo.id)
            else:
                notification_service.create_notification(
                    user_id=todo.assignee_id,
                    title="你有一个待办已超时",
                    content=f"{todo.title} 已超过截止时间，请尽快处理。",
                    biz_type=todo.business_type,
                    biz_id=todo.business_id,
                )
                notification_created += 1
            if todo.business_type == "ticket":
                self._sync_ticket_overdue_from_todo(todo)

        self.db.flush()
        result = TodoTimeoutCheckResult(
            scanned=len(todos),
            expired=expired_count,
            notification_created=notification_created,
            skipped=skipped,
        )
        logger.info(
            "[Todo Timeout] scanned=%s expired=%s notification_created=%s skipped=%s",
            result.scanned,
            result.expired,
            result.notification_created,
            result.skipped,
        )
        logger.info("[Todo Timeout] finished")
        return result

    def _list(
        self,
        *,
        assignee_id: int | None = None,
        status: str | None = None,
        todo_type: str | None = None,
        business_type: str | None = None,
        priority: str | None = None,
        keyword: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Todo], int]:
        stmt = select(Todo).where(Todo.is_deleted == 0)
        if assignee_id is not None:
            stmt = stmt.where(Todo.assignee_id == assignee_id)
        if status:
            stmt = stmt.where(Todo.status == status)
        if todo_type:
            stmt = stmt.where(Todo.todo_type == todo_type)
        if business_type:
            stmt = stmt.where(Todo.business_type == business_type)
        if priority:
            stmt = stmt.where(Todo.priority == priority)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(Todo.title.like(like), Todo.content.like(like)))
        if start_date:
            stmt = stmt.where(Todo.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Todo.created_at <= end_date)

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Todo.created_at.desc(), Todo.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        self._attach_business_info(items)
        return items, total

    def _count(self, stmt: object) -> int:
        return self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    def _admin_users(self) -> list[User]:
        stmt = (
            select(User)
            .join(SysUserRole, SysUserRole.user_id == User.id)
            .join(SysRole, SysRole.id == SysUserRole.role_id)
            .where(User.status == 1, SysRole.status == 1, SysRole.role_code == "admin")
        )
        return list(self.db.scalars(stmt))

    def _attach_business_info(self, todos: list[Todo]) -> None:
        ticket_ids = [
            todo.business_id
            for todo in todos
            if todo.business_type == "ticket" and todo.business_id
        ]
        if not ticket_ids:
            return
        tickets = {
            ticket.id: ticket
            for ticket in self.db.scalars(select(Ticket).where(Ticket.id.in_(ticket_ids)))
        }
        for todo in todos:
            ticket = tickets.get(todo.business_id)
            if ticket is not None:
                todo.business_title = ticket.title
                todo.business_status = ticket.status

    def _active_business_todos(
        self,
        *,
        business_type: str,
        business_id: int,
        todo_type: str | None = None,
        assignee_id: int | None = None,
    ) -> list[Todo]:
        stmt = select(Todo).where(
            Todo.business_type == business_type,
            Todo.business_id == business_id,
            Todo.status.in_(list(ACTIVE_TODO_STATUSES)),
            Todo.is_deleted == 0,
        )
        if todo_type:
            stmt = stmt.where(Todo.todo_type == todo_type)
        if assignee_id is not None:
            stmt = stmt.where(Todo.assignee_id == assignee_id)
        return list(self.db.scalars(stmt))

    def _cancel_todo(self, todo: Todo, *, remark: str | None = None) -> None:
        todo.status = TodoStatus.CANCELLED
        todo.cancelled_at = local_now()
        if remark:
            todo.remark = remark

    def _sync_ticket_overdue_from_todo(self, todo: Todo) -> None:
        ticket = self.db.get(Ticket, todo.business_id)
        if ticket is None:
            return
        if todo.todo_type in {"ticket_assign", "ticket_accept"} and ticket.response_overdue == 0:
            ticket.response_overdue = 1
        if todo.todo_type == "ticket_process" and ticket.resolve_overdue == 0:
            ticket.resolve_overdue = 1

    def _generate_todo_no(self) -> str:
        today = local_now().strftime("%Y%m%d")
        prefix = f"TODO{today}"
        latest_no = self.db.scalar(
            select(func.max(Todo.todo_no)).where(Todo.todo_no.like(f"{prefix}%"))
        )
        sequence = int(latest_no[-4:]) + 1 if latest_no else 1
        return f"{prefix}{sequence:04d}"


def check_todo_timeout(db: Session) -> TodoTimeoutCheckResult:
    return TodoService(db).check_todo_timeout()
