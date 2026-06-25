from collections.abc import Iterator
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models import (
    Notification,
    SysRole,
    SysUserRole,
    Ticket,
    TicketCategory,
    Todo,
    TodoStatus,
    User,
)
from app.models import __all__ as _model_exports
from app.schemas.ticket import TicketAssign, TicketComplete, TicketCreate, TicketStart
from app.services.ticket_service import TicketService
from app.services.todo_service import TodoService
from app.utils.timezone import local_now

_ = _model_exports
DEFAULT_HASH = "md5$e10adc3949ba59abbe56e057f20f883e"


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        session.add_all(
            [
                User(
                    id=1,
                    username="admin",
                    password_hash=DEFAULT_HASH,
                    real_name="admin",
                    role="admin",
                    status=1,
                ),
                User(
                    id=2,
                    username="handler",
                    password_hash=DEFAULT_HASH,
                    real_name="handler",
                    role="it_staff",
                    status=1,
                ),
                User(
                    id=3,
                    username="reporter",
                    password_hash=DEFAULT_HASH,
                    real_name="reporter",
                    role="employee",
                    status=1,
                ),
                SysRole(id=1, role_code="admin", role_name="管理员", status=1),
                SysUserRole(id=1, user_id=1, role_id=1),
                TicketCategory(id=1, name="打印机故障", code="printer", status=1),
            ]
        )
        session.commit()
        yield session
    finally:
        session.close()
        engine.dispose()


def test_create_for_business_avoids_duplicate_active_todos(db_session: Session) -> None:
    service = TodoService(db_session)

    first = service.create_for_business(
        title="todo",
        content="todo content",
        todo_type="ticket_process",
        business_type="ticket",
        business_id=1,
        assignee_id=2,
    )
    second = service.create_for_business(
        title="todo duplicated",
        content="todo content",
        todo_type="ticket_process",
        business_type="ticket",
        business_id=1,
        assignee_id=2,
    )
    db_session.commit()

    assert first.id == second.id
    assert db_session.query(Todo).count() == 1


def test_ticket_flow_creates_and_closes_todos(db_session: Session) -> None:
    ticket = TicketService(db_session).create(
        TicketCreate(
            title="printer broken",
            description="printer broken",
            category_id=1,
            reporter_id=3,
        )
    )
    assign_todo = db_session.query(Todo).filter_by(todo_type="ticket_assign").one()
    assert assign_todo.assignee_id == 1
    assert assign_todo.status == TodoStatus.PENDING

    TicketService(db_session).assign(ticket.id, TicketAssign(handler_id=2), operator_id=1)
    db_session.refresh(assign_todo)
    process_todo = db_session.query(Todo).filter_by(todo_type="ticket_process").one()
    assert assign_todo.status == TodoStatus.CANCELLED
    assert process_todo.assignee_id == 2
    assert process_todo.status == TodoStatus.PENDING

    TicketService(db_session).start(ticket.id, TicketStart(), db_session.get(User, 2))
    db_session.refresh(process_todo)
    assert process_todo.status == TodoStatus.PROCESSING

    TicketService(db_session).complete(
        ticket.id,
        TicketComplete(
            result="done",
            repair_result="fixed",
            repair_cost=Decimal("0.00"),
        ),
        db_session.get(User, 2),
    )
    db_session.refresh(process_todo)
    confirm_todo = db_session.query(Todo).filter_by(todo_type="ticket_confirm").one()
    assert process_todo.status == TodoStatus.COMPLETED
    assert confirm_todo.assignee_id == 3
    assert confirm_todo.status == TodoStatus.PENDING


def test_check_todo_timeout_expires_todo_and_sends_notification(db_session: Session) -> None:
    db_session.add(
        Ticket(
            id=1,
            ticket_no="TK1",
            title="overdue ticket",
            description="test",
            category_id=1,
            reporter_id=3,
            handler_id=2,
        )
    )
    service = TodoService(db_session)
    service.create_for_business(
        title="overdue todo",
        content="overdue todo",
        todo_type="ticket_process",
        business_type="ticket",
        business_id=1,
        assignee_id=2,
        deadline_at=datetime.now() - timedelta(minutes=1),
    )
    db_session.commit()

    result = service.check_todo_timeout()
    db_session.commit()

    todo = db_session.query(Todo).one()
    ticket = db_session.get(Ticket, 1)
    notification = db_session.query(Notification).one()
    assert result.scanned == 1
    assert result.expired == 1
    assert result.notification_created == 1
    assert todo.status == TodoStatus.EXPIRED
    assert todo.expire_notice_sent == 1
    assert ticket.resolve_overdue == 1
    assert notification.title == "你有一个待办已超时"


def test_my_statistics_counts_current_user_todos(db_session: Session) -> None:
    now = local_now().replace(hour=12, minute=0, second=0, microsecond=0)
    service = TodoService(db_session)
    service.create_for_business(
        title="pending",
        content="pending",
        todo_type="ticket_process",
        business_type="ticket",
        business_id=1,
        assignee_id=2,
        priority="urgent",
        deadline_at=now + timedelta(hours=1),
    )
    service.create_for_business(
        title="processing",
        content="processing",
        todo_type="ticket_process",
        business_type="ticket",
        business_id=2,
        assignee_id=2,
    ).status = TodoStatus.PROCESSING
    service.create_for_business(
        title="expired",
        content="expired",
        todo_type="ticket_process",
        business_type="ticket",
        business_id=3,
        assignee_id=2,
    ).status = TodoStatus.EXPIRED
    db_session.commit()

    stats = service.statistics(2)

    assert stats == {
        "pending_count": 1,
        "processing_count": 1,
        "expired_count": 1,
        "today_deadline_count": 1,
        "urgent_count": 1,
    }
