from collections.abc import Iterator
from datetime import timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models import (
    Notification,
    SysRole,
    SysUserRole,
    Ticket,
    TicketAssignmentLog,
    TicketAssignmentRule,
    TicketStatus,
    Todo,
    TodoStatus,
    User,
    WorkGroup,
    WorkGroupMember,
)
from app.models import __all__ as _model_exports
from app.services.ticket_assignment_service import TicketAssignmentService
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
                    real_name="管理员",
                    role="admin",
                    status=1,
                ),
                User(
                    id=2,
                    username="it_a",
                    password_hash=DEFAULT_HASH,
                    real_name="运维A",
                    role="it_staff",
                    status=1,
                ),
                User(
                    id=3,
                    username="it_b",
                    password_hash=DEFAULT_HASH,
                    real_name="运维B",
                    role="it_staff",
                    status=1,
                ),
                User(
                    id=4,
                    username="employee",
                    password_hash=DEFAULT_HASH,
                    real_name="员工",
                    role="employee",
                    status=1,
                ),
                User(
                    id=5,
                    username="disabled",
                    password_hash=DEFAULT_HASH,
                    real_name="禁用运维",
                    role="it_staff",
                    status=0,
                ),
                SysRole(id=1, role_code="admin", role_name="管理员", status=1),
                SysRole(id=2, role_code="it_staff", role_name="IT运维", status=1),
                SysRole(id=3, role_code="employee", role_name="员工", status=1),
                SysUserRole(id=1, user_id=1, role_id=1),
                SysUserRole(id=2, user_id=2, role_id=2),
                SysUserRole(id=3, user_id=3, role_id=2),
                SysUserRole(id=4, user_id=4, role_id=3),
                SysUserRole(id=5, user_id=5, role_id=2),
                WorkGroup(id=1, group_name="桌面运维组", group_code="desktop", status=1),
                WorkGroup(id=2, group_name="网络运维组", group_code="network", status=1),
                WorkGroupMember(id=1, group_id=1, user_id=2, status=1),
                WorkGroupMember(id=2, group_id=1, user_id=3, status=1),
                WorkGroupMember(id=3, group_id=2, user_id=2, status=1),
            ]
        )
        session.commit()
        yield session
    finally:
        session.close()
        engine.dispose()


def add_ticket(
    session: Session,
    ticket_id: int,
    *,
    category_id: int | None = 1,
    priority: str = "normal",
    handler_id: int | None = None,
    status: TicketStatus = TicketStatus.PENDING_ACCEPT,
    assigned_offset_minutes: int | None = None,
) -> Ticket:
    assigned_at = (
        local_now() + timedelta(minutes=assigned_offset_minutes)
        if assigned_offset_minutes is not None
        else None
    )
    ticket = Ticket(
        id=ticket_id,
        ticket_no=f"TK{ticket_id:04d}",
        title=f"ticket-{ticket_id}",
        description="test",
        category_id=category_id,
        priority=priority,
        status=status,
        reporter_id=4,
        handler_id=handler_id,
        assigned_at=assigned_at,
    )
    session.add(ticket)
    session.flush()
    return ticket


def add_rule(
    session: Session,
    *,
    rule_id: int = 1,
    category_id: int | None = 1,
    priority: str | None = None,
    ops_group_id: int | None = 1,
    assign_strategy: str = "least_workload",
    target_user_id: int | None = None,
    enabled: int = 1,
    sort_order: int = 10,
) -> TicketAssignmentRule:
    rule = TicketAssignmentRule(
        id=rule_id,
        name=f"rule-{rule_id}",
        category_id=category_id,
        priority=priority,
        ops_group_id=ops_group_id,
        assign_strategy=assign_strategy,
        target_user_id=target_user_id,
        enabled=enabled,
        sort_order=sort_order,
    )
    session.add(rule)
    session.flush()
    return rule


def test_least_workload_assigns_user_with_fewer_unfinished_tickets(
    db_session: Session,
) -> None:
    add_rule(db_session)
    add_ticket(
        db_session,
        10,
        handler_id=2,
        status=TicketStatus.ASSIGNED,
        assigned_offset_minutes=-10,
    )
    ticket = add_ticket(db_session, 1)

    result = TicketAssignmentService(db_session).auto_assign_ticket(ticket)

    assert result.success is True
    assert ticket.status == TicketStatus.ASSIGNED
    assert ticket.handler_id == 3
    assert ticket.assign_type == "auto"
    assert ticket.accepted_at is None
    assert db_session.query(TicketAssignmentLog).filter_by(success=1).count() == 1
    assert db_session.query(Todo).filter_by(assignee_id=3, todo_type="ticket_process").count() == 1
    assert db_session.query(Notification).filter_by(user_id=3, title="新的工单分配").count() == 1


def test_least_workload_tie_uses_oldest_last_assigned_then_user_id(
    db_session: Session,
) -> None:
    add_rule(db_session)
    add_ticket(
        db_session,
        20,
        handler_id=2,
        status=TicketStatus.COMPLETED,
        assigned_offset_minutes=-5,
    )
    add_ticket(
        db_session,
        21,
        handler_id=3,
        status=TicketStatus.COMPLETED,
        assigned_offset_minutes=-60,
    )
    ticket = add_ticket(db_session, 1)

    result = TicketAssignmentService(db_session).auto_assign_ticket(ticket)

    assert result.success is True
    assert ticket.handler_id == 3


def test_fixed_user_assigns_target_user(db_session: Session) -> None:
    add_rule(
        db_session,
        assign_strategy="fixed_user",
        target_user_id=2,
        ops_group_id=1,
    )
    ticket = add_ticket(db_session, 1)

    result = TicketAssignmentService(db_session).auto_assign_ticket(ticket)

    assert result.success is True
    assert ticket.handler_id == 2
    assert result.assign_strategy == "fixed_user"


def test_fixed_user_missing_target_fails_and_keeps_ticket_pending_accept(
    db_session: Session,
) -> None:
    add_rule(db_session, assign_strategy="fixed_user", target_user_id=999, ops_group_id=None)
    ticket = add_ticket(db_session, 1)

    result = TicketAssignmentService(db_session).auto_assign_ticket(ticket)

    assert result.success is False
    assert result.fail_stage == "check_user"
    assert ticket.status == TicketStatus.PENDING_ACCEPT
    assert ticket.handler_id is None
    assert db_session.query(TicketAssignmentLog).filter_by(success=0).count() == 1


def test_fixed_user_disabled_target_fails(db_session: Session) -> None:
    add_rule(db_session, assign_strategy="fixed_user", target_user_id=5, ops_group_id=None)
    ticket = add_ticket(db_session, 1)

    result = TicketAssignmentService(db_session).auto_assign_ticket(ticket)

    assert result.success is False
    assert result.fail_reason == "固定处理人账号已禁用"


def test_fixed_user_non_it_target_fails(db_session: Session) -> None:
    add_rule(db_session, assign_strategy="fixed_user", target_user_id=4, ops_group_id=None)
    ticket = add_ticket(db_session, 1)

    result = TicketAssignmentService(db_session).auto_assign_ticket(ticket)

    assert result.success is False
    assert result.fail_reason == "固定处理人不是 IT 运维人员"


def test_no_matching_rule_fails(db_session: Session) -> None:
    ticket = add_ticket(db_session, 1)

    result = TicketAssignmentService(db_session).auto_assign_ticket(ticket)

    assert result.success is False
    assert result.fail_stage == "match_rule"
    assert ticket.status == TicketStatus.PENDING_ACCEPT


def test_force_false_rejects_existing_assignee(db_session: Session) -> None:
    add_rule(db_session)
    ticket = add_ticket(db_session, 1, handler_id=2, status=TicketStatus.ASSIGNED)

    result = TicketAssignmentService(db_session).auto_assign_ticket(ticket, force=False)

    assert result.success is False
    assert result.fail_reason == "工单已经存在处理人，不能重复自动分配"
    assert ticket.handler_id == 2


def test_force_true_reassigns_and_cancels_old_todo(db_session: Session) -> None:
    add_rule(db_session)
    ticket = add_ticket(db_session, 1, handler_id=2, status=TicketStatus.ASSIGNED)
    TodoService(db_session).create_for_business(
        title="old todo",
        content="old todo",
        todo_type="ticket_process",
        business_type="ticket",
        business_id=1,
        assignee_id=2,
    )
    add_ticket(
        db_session,
        30,
        handler_id=2,
        status=TicketStatus.ASSIGNED,
        assigned_offset_minutes=-1,
    )

    result = TicketAssignmentService(db_session).auto_assign_ticket(ticket, force=True)

    old_todo = db_session.query(Todo).filter_by(assignee_id=2, business_id=1).one()
    assert result.success is True
    assert ticket.handler_id == 3
    assert old_todo.status == TodoStatus.CANCELLED
    assert db_session.query(Notification).filter_by(user_id=2, title="工单已重新分配").count() == 1
