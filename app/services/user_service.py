from __future__ import annotations

from typing import Any

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Asset,
    OperationLog,
    RepairRecord,
    SysRole,
    SysUserRole,
    Ticket,
    TicketStatus,
    User,
)
from app.schemas.user import UserCreate, UserUpdate

UNFINISHED_TICKET_STATUSES = {
    TicketStatus.PENDING,
    TicketStatus.PENDING_ACCEPT,
    TicketStatus.ASSIGNED,
    TicketStatus.PROCESSING,
    TicketStatus.PENDING_CONFIRM,
}


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: UserCreate) -> User:
        data = payload.model_dump()
        password = data.pop("password")
        user = User(**data, password_hash=hash_password(password))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def list(
        self,
        *,
        keyword: str | None = None,
        role: str | None = None,
        status: int | None = None,
        department: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[User], int]:
        stmt = select(User)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(
                or_(User.username.like(like), User.real_name.like(like), User.phone.like(like))
            )
        if role:
            stmt = stmt.where(User.role == role)
        if status is not None:
            stmt = stmt.where(User.status == status)
        if department:
            stmt = stmt.where(User.department == department)

        total = len(list(self.db.scalars(stmt)))
        items = list(
            self.db.scalars(
                stmt.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
            )
        )
        return items, total

    def update(self, user_id: int, payload: UserUpdate) -> User | None:
        user = self.get(user_id)
        if user is None:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_status(self, user_id: int, status: int) -> User | None:
        user = self.get(user_id)
        if user is None:
            return None
        user.status = status
        self.db.commit()
        self.db.refresh(user)
        return user

    def reset_password(self, user_id: int, new_password: str) -> User | None:
        user = self.get(user_id)
        if user is None:
            return None
        user.password_hash = hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)
        return user

    def has_related_data(self, user_id: int) -> bool:
        checks = [
            select(Ticket.id).where(Ticket.reporter_id == user_id),
            select(Ticket.id).where(Ticket.handler_id == user_id),
            select(Asset.id).where(Asset.user_id == user_id),
            select(RepairRecord.id).where(RepairRecord.repair_user_id == user_id),
        ]
        return any(self.db.scalar(stmt.limit(1)) is not None for stmt in checks)

    def batch_delete(self, ids: list[int], current_user_id: int) -> dict[str, Any]:
        deleted_count = 0
        failed_items: list[dict[str, int | str]] = []

        for user_id in self._deduplicate_ids(ids):
            user = self.get(user_id)
            if user is None:
                failed_items.append({"id": user_id, "reason": "用户不存在"})
                continue
            if user_id == current_user_id:
                failed_items.append({"id": user_id, "reason": "不能删除当前登录用户"})
                continue
            if self.is_super_admin(user):
                failed_items.append({"id": user_id, "reason": "不能删除超级管理员"})
                continue
            if self.has_unfinished_tickets(user_id):
                failed_items.append({"id": user_id, "reason": "存在未完成工单，无法删除"})
                continue
            if self.has_physical_delete_blockers(user_id):
                failed_items.append({"id": user_id, "reason": "用户已关联业务数据，无法删除"})
                continue

            self.db.execute(delete(SysUserRole).where(SysUserRole.user_id == user_id))
            self.db.delete(user)
            deleted_count += 1

        self.db.flush()
        return {"deleted_count": deleted_count, "failed_items": failed_items}

    def has_unfinished_tickets(self, user_id: int) -> bool:
        stmt = (
            select(Ticket.id)
            .where(
                or_(Ticket.reporter_id == user_id, Ticket.handler_id == user_id),
                Ticket.status.in_(UNFINISHED_TICKET_STATUSES),
            )
            .limit(1)
        )
        return self.db.scalar(stmt) is not None

    def has_physical_delete_blockers(self, user_id: int) -> bool:
        checks = [
            select(Ticket.id).where(
                or_(Ticket.reporter_id == user_id, Ticket.handler_id == user_id)
            ),
            select(Asset.id).where(Asset.user_id == user_id),
            select(RepairRecord.id).where(RepairRecord.repair_user_id == user_id),
            select(OperationLog.id).where(OperationLog.user_id == user_id),
        ]
        return any(self.db.scalar(stmt.limit(1)) is not None for stmt in checks)

    def is_super_admin(self, user: User) -> bool:
        role_value = getattr(user.role, "value", user.role)
        if user.id == 1 or role_value == "admin":
            return True
        stmt = (
            select(SysRole.id)
            .join(SysUserRole, SysUserRole.role_id == SysRole.id)
            .where(SysUserRole.user_id == user.id, SysRole.role_code == "admin")
            .limit(1)
        )
        return self.db.scalar(stmt) is not None

    def delete(self, user_id: int) -> bool:
        user = self.get(user_id)
        if user is None:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

    def _deduplicate_ids(self, ids: list[int]) -> list[int]:
        seen: set[int] = set()
        deduplicated = []
        for item_id in ids:
            if item_id not in seen:
                deduplicated.append(item_id)
                seen.add(item_id)
        return deduplicated
