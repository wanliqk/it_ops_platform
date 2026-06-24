from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models import SlaRule, Ticket, TicketPriority, TicketStatus, User
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
