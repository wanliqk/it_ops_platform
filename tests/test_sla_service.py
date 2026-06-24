from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models import Notification, SlaRule, Ticket, TicketPriority, TicketStatus, User
from app.models import __all__ as _model_exports
from app.schemas.ticket import TicketAssign, TicketComplete, TicketCreate, TicketStart
from app.services.sla_service import SlaService
from app.services.ticket_service import TicketService

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
                    username="reporter",
                    password_hash=DEFAULT_HASH,
                    real_name="reporter",
                    role="employee",
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
            ]
        )
        session.commit()
        yield session
    finally:
        session.close()
        engine.dispose()


def add_rule(
    session: Session,
    *,
    rule_id: int,
    priority: str,
    response_minutes: int,
    resolve_minutes: int,
    ticket_category: str | None = None,
    sort_order: int = 10,
    enabled: int = 1,
) -> None:
    session.add(
        SlaRule(
            id=rule_id,
            name=f"rule-{rule_id}",
            ticket_category=ticket_category,
            priority=priority,
            response_minutes=response_minutes,
            resolve_minutes=resolve_minutes,
            enabled=enabled,
            sort_order=sort_order,
        )
    )


def test_specific_sla_rule_has_priority_over_common_rule(db_session: Session) -> None:
    add_rule(
        db_session,
        rule_id=1,
        ticket_category=None,
        priority="urgent",
        response_minutes=10,
        resolve_minutes=120,
        sort_order=1,
    )
    add_rule(
        db_session,
        rule_id=2,
        ticket_category="network",
        priority="urgent",
        response_minutes=5,
        resolve_minutes=60,
        sort_order=99,
    )
    db_session.commit()

    created_at = datetime(2026, 6, 24, 10, 0, tzinfo=UTC)
    response_deadline, resolve_deadline = SlaService(db_session).calculate_ticket_sla_deadline(
        created_at=created_at,
        ticket_category="network",
        priority="urgent",
    )

    assert response_deadline == created_at + timedelta(minutes=5)
    assert resolve_deadline == created_at + timedelta(minutes=60)


def test_common_sla_rule_is_used_when_specific_rule_missing(db_session: Session) -> None:
    add_rule(
        db_session,
        rule_id=1,
        priority="medium",
        response_minutes=60,
        resolve_minutes=480,
    )
    db_session.commit()

    created_at = datetime(2026, 6, 24, 10, 0, tzinfo=UTC)
    response_deadline, resolve_deadline = SlaService(db_session).calculate_ticket_sla_deadline(
        created_at=created_at,
        ticket_category="software",
        priority="normal",
    )

    assert response_deadline == created_at + timedelta(minutes=60)
    assert resolve_deadline == created_at + timedelta(minutes=480)


def test_default_sla_deadline_is_used_when_no_rule_matches(db_session: Session) -> None:
    created_at = datetime(2026, 6, 24, 10, 0, tzinfo=UTC)
    response_deadline, resolve_deadline = SlaService(db_session).calculate_ticket_sla_deadline(
        created_at=created_at,
        ticket_category="software",
        priority="high",
    )

    assert response_deadline == created_at + timedelta(minutes=60)
    assert resolve_deadline == created_at + timedelta(minutes=480)


def test_ticket_create_writes_sla_deadlines(db_session: Session) -> None:
    add_rule(
        db_session,
        rule_id=1,
        priority="medium",
        response_minutes=30,
        resolve_minutes=90,
    )
    db_session.commit()

    ticket = TicketService(db_session).create(
        TicketCreate(
            title="test",
            description="test",
            fault_type="software",
            priority=TicketPriority.NORMAL,
            reporter_id=1,
        )
    )

    assert ticket.sla_response_deadline - ticket.created_at == timedelta(minutes=30)
    assert ticket.sla_resolve_deadline - ticket.created_at == timedelta(minutes=90)


def test_first_response_at_is_written_only_once(db_session: Session) -> None:
    db_session.add(
        Ticket(
            id=1,
            ticket_no="TK1",
            title="test",
            description="test",
            status=TicketStatus.PENDING,
            reporter_id=1,
        )
    )
    db_session.commit()

    service = TicketService(db_session)
    assigned = service.assign(1, TicketAssign(handler_id=2), operator_id=1)
    first_response_at = assigned.first_response_at
    started = service.start(1, TicketStart(), operator=db_session.get(User, 2))

    assert first_response_at is not None
    assert started.first_response_at == first_response_at


def test_complete_writes_resolved_at(db_session: Session) -> None:
    db_session.add(
        Ticket(
            id=1,
            ticket_no="TK1",
            title="test",
            description="test",
            status=TicketStatus.PROCESSING,
            reporter_id=1,
            handler_id=2,
        )
    )
    db_session.commit()

    completed = TicketService(db_session).complete(
        1,
        TicketComplete(
            result="done",
            repair_result="fixed",
            repair_cost=Decimal("0.00"),
        ),
        operator=db_session.get(User, 2),
    )

    assert completed.status == TicketStatus.COMPLETED
    assert completed.resolved_at == completed.completed_at


def test_check_ticket_sla_timeout_marks_overdue_and_creates_notifications(
    db_session: Session,
) -> None:
    now = datetime.now()
    db_session.add(
        Ticket(
            id=1,
            ticket_no="TK1",
            title="overdue",
            description="test",
            status=TicketStatus.PENDING,
            reporter_id=1,
            handler_id=2,
            sla_response_deadline=now - timedelta(minutes=10),
            sla_resolve_deadline=now - timedelta(minutes=5),
        )
    )
    db_session.commit()

    result = SlaService(db_session).check_ticket_sla_timeout()
    db_session.commit()

    ticket = db_session.get(Ticket, 1)
    notifications = db_session.query(Notification).order_by(Notification.id).all()
    assert result.scanned == 1
    assert result.response_overdue == 1
    assert result.resolve_overdue == 1
    assert result.notification_created == 2
    assert result.skipped == 0
    assert ticket.response_overdue == 1
    assert ticket.resolve_overdue == 1
    assert [item.title for item in notifications] == ["工单响应已超时", "工单处理已超时"]
    assert {item.user_id for item in notifications} == {2}


def test_check_ticket_sla_timeout_does_not_create_duplicate_notifications(
    db_session: Session,
) -> None:
    now = datetime.now()
    db_session.add(
        Ticket(
            id=1,
            ticket_no="TK1",
            title="overdue",
            description="test",
            status=TicketStatus.PENDING,
            reporter_id=1,
            sla_response_deadline=now - timedelta(minutes=10),
            sla_resolve_deadline=now - timedelta(minutes=5),
        )
    )
    db_session.commit()

    first_result = SlaService(db_session).check_ticket_sla_timeout()
    second_result = SlaService(db_session).check_ticket_sla_timeout()
    db_session.commit()

    notifications = db_session.query(Notification).all()
    assert first_result.response_overdue == 1
    assert first_result.resolve_overdue == 1
    assert first_result.notification_created == 2
    assert second_result.response_overdue == 0
    assert second_result.resolve_overdue == 0
    assert second_result.notification_created == 0
    assert len(notifications) == 2


def test_check_ticket_sla_timeout_skips_finished_tickets(db_session: Session) -> None:
    now = datetime.now()
    db_session.add_all(
        [
            Ticket(
                id=1,
                ticket_no="TK1",
                title="completed",
                description="test",
                status=TicketStatus.COMPLETED,
                reporter_id=1,
                sla_response_deadline=now - timedelta(minutes=10),
                sla_resolve_deadline=now - timedelta(minutes=5),
            ),
            Ticket(
                id=2,
                ticket_no="TK2",
                title="cancelled",
                description="test",
                status=TicketStatus.CANCELLED,
                reporter_id=1,
                sla_response_deadline=now - timedelta(minutes=10),
                sla_resolve_deadline=now - timedelta(minutes=5),
            ),
        ]
    )
    db_session.commit()

    result = SlaService(db_session).check_ticket_sla_timeout()
    db_session.commit()

    assert result.scanned == 0
    assert db_session.get(Ticket, 1).response_overdue == 0
    assert db_session.get(Ticket, 2).resolve_overdue == 0
    assert db_session.query(Notification).count() == 0


def test_check_ticket_sla_timeout_does_not_mark_responded_ticket(
    db_session: Session,
) -> None:
    now = datetime.now()
    db_session.add(
        Ticket(
            id=1,
            ticket_no="TK1",
            title="responded",
            description="test",
            status=TicketStatus.PROCESSING,
            reporter_id=1,
            handler_id=2,
            first_response_at=now - timedelta(minutes=20),
            sla_response_deadline=now - timedelta(minutes=10),
            sla_resolve_deadline=now + timedelta(minutes=10),
        )
    )
    db_session.commit()

    result = SlaService(db_session).check_ticket_sla_timeout()
    db_session.commit()

    ticket = db_session.get(Ticket, 1)
    assert result.scanned == 0
    assert result.response_overdue == 0
    assert result.notification_created == 0
    assert ticket.response_overdue == 0
    assert db_session.query(Notification).count() == 0


def test_check_ticket_sla_timeout_does_not_mark_resolved_ticket(
    db_session: Session,
) -> None:
    now = datetime.now()
    db_session.add(
        Ticket(
            id=1,
            ticket_no="TK1",
            title="resolved",
            description="test",
            status=TicketStatus.PROCESSING,
            reporter_id=1,
            handler_id=2,
            first_response_at=now - timedelta(minutes=30),
            resolved_at=now - timedelta(minutes=1),
            sla_response_deadline=now - timedelta(minutes=20),
            sla_resolve_deadline=now - timedelta(minutes=10),
        )
    )
    db_session.commit()

    result = SlaService(db_session).check_ticket_sla_timeout()
    db_session.commit()

    ticket = db_session.get(Ticket, 1)
    assert result.scanned == 0
    assert result.resolve_overdue == 0
    assert result.notification_created == 0
    assert ticket.resolve_overdue == 0
    assert db_session.query(Notification).count() == 0
