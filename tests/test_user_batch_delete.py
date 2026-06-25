from collections.abc import Iterator

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models import Ticket, TicketCategory, TicketStatus, User
from app.models import __all__ as _model_exports
from app.schemas.user import UserBatchDeleteRequest
from app.services.user_service import UserService

_ = _model_exports


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        session.add(TicketCategory(id=1, name="默认分类", code="default", status=1))
        session.commit()
        yield session
    finally:
        session.close()
        engine.dispose()


def add_user(session: Session, user_id: int, username: str, role: str = "employee") -> User:
    user = User(
        id=user_id,
        username=username,
        password_hash="md5$e10adc3949ba59abbe56e057f20f883e",
        real_name=username,
        role=role,
        status=1,
    )
    session.add(user)
    return user


def add_ticket(session: Session, ticket_id: int, reporter_id: int, status: TicketStatus) -> None:
    session.add(
        Ticket(
            id=ticket_id,
            ticket_no=f"TK{ticket_id:04d}",
            title="test ticket",
            description="test ticket",
            category_id=1,
            status=status,
            reporter_id=reporter_id,
        )
    )


def test_batch_delete_users_physically_deletes_allowed_users(db_session: Session) -> None:
    add_user(db_session, 99, "operator")
    add_user(db_session, 2, "employee_a")
    add_user(db_session, 3, "employee_b")
    db_session.commit()

    result = UserService(db_session).batch_delete([2, 3], current_user_id=99)
    db_session.commit()

    assert result == {"deleted_count": 2, "failed_items": []}
    assert db_session.get(User, 2) is None
    assert db_session.get(User, 3) is None


def test_batch_delete_users_returns_failed_items(db_session: Session) -> None:
    add_user(db_session, 1, "admin", role="admin")
    add_user(db_session, 2, "operator")
    add_user(db_session, 3, "has_ticket")
    add_user(db_session, 4, "employee")
    add_ticket(db_session, 1, reporter_id=3, status=TicketStatus.PENDING)
    db_session.commit()

    result = UserService(db_session).batch_delete([1, 2, 3, 4, 404], current_user_id=2)
    db_session.commit()

    assert result == {
        "deleted_count": 1,
        "failed_items": [
            {"id": 1, "reason": "不能删除超级管理员"},
            {"id": 2, "reason": "不能删除当前登录用户"},
            {"id": 3, "reason": "存在未完成工单，无法删除"},
            {"id": 404, "reason": "用户不存在"},
        ],
    }
    assert db_session.get(User, 1).status == 1
    assert db_session.get(User, 2).status == 1
    assert db_session.get(User, 3).status == 1
    assert db_session.get(User, 4) is None


def test_batch_delete_users_rejects_related_completed_ticket_users(db_session: Session) -> None:
    add_user(db_session, 99, "operator")
    add_user(db_session, 3, "completed_ticket_user")
    add_ticket(db_session, 1, reporter_id=3, status=TicketStatus.COMPLETED)
    db_session.commit()

    result = UserService(db_session).batch_delete([3], current_user_id=99)

    assert result == {
        "deleted_count": 0,
        "failed_items": [{"id": 3, "reason": "用户已关联业务数据，无法删除"}],
    }
    assert db_session.get(User, 3).status == 1


def test_batch_delete_request_allows_at_most_100_ids() -> None:
    with pytest.raises(ValidationError):
        UserBatchDeleteRequest(ids=list(range(101)))
