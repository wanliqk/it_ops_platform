from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Ticket, TicketCategory, User, WorkGroup
from app.schemas.ticket_category_schema import TicketCategoryCreate, TicketCategoryUpdate


class TicketCategoryConflictError(Exception):
    pass


class TicketCategoryNotFoundError(Exception):
    pass


class TicketCategoryValidationError(Exception):
    pass


class TicketCategoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_categories(
        self,
        *,
        keyword: str | None = None,
        status: int | None = None,
        parent_id: int | None = None,
    ) -> list[TicketCategory]:
        stmt = select(TicketCategory)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(TicketCategory.name.like(like), TicketCategory.code.like(like)))
        if status is not None:
            stmt = stmt.where(TicketCategory.status == status)
        if parent_id is not None:
            stmt = stmt.where(TicketCategory.parent_id == parent_id)
        return list(
            self.db.scalars(
                stmt.order_by(TicketCategory.sort_order.asc(), TicketCategory.id.asc())
            )
        )

    def tree(self, *, status: int | None = None) -> list[TicketCategory]:
        categories = self.list_categories(status=status)
        by_parent: dict[int | None, list[TicketCategory]] = {}
        for category in categories:
            by_parent.setdefault(category.parent_id, []).append(category)
        for category in categories:
            category.children = by_parent.get(category.id, [])
        return by_parent.get(None, [])

    def get(self, category_id: int) -> TicketCategory | None:
        return self.db.get(TicketCategory, category_id)

    def create(self, payload: TicketCategoryCreate) -> TicketCategory:
        data = payload.model_dump()
        self._validate_unique_code(data["code"])
        self._validate_refs(data)
        category = TicketCategory(**data)
        self.db.add(category)
        self.db.flush()
        return category

    def update(
        self,
        category_id: int,
        payload: TicketCategoryUpdate,
    ) -> TicketCategory | None:
        category = self.get(category_id)
        if category is None:
            return None
        data = payload.model_dump(exclude_unset=True)
        merged = {
            "parent_id": category.parent_id,
            "name": category.name,
            "code": category.code,
            "description": category.description,
            "default_priority": category.default_priority,
            "default_group_id": category.default_group_id,
            "assignment_strategy": category.assignment_strategy,
            "fixed_assignee_id": category.fixed_assignee_id,
            "require_asset": category.require_asset,
            "sort_order": category.sort_order,
            "status": category.status,
        } | data
        if "code" in data and data["code"] != category.code:
            self._validate_unique_code(data["code"], exclude_id=category_id)
        self._validate_parent(category_id, merged.get("parent_id"))
        self._validate_refs(merged)
        for field, value in data.items():
            setattr(category, field, value)
        self.db.flush()
        return category

    def update_status(self, category_id: int, status: int) -> TicketCategory | None:
        category = self.get(category_id)
        if category is None:
            return None
        category.status = status
        self.db.flush()
        return category

    def delete(self, category_id: int) -> bool:
        category = self.get(category_id)
        if category is None:
            return False
        if self.has_children(category_id):
            raise TicketCategoryConflictError("该分类下存在子分类，无法删除")
        if self.has_tickets(category_id):
            raise TicketCategoryConflictError("该分类已被工单使用，无法删除")
        category.status = 0
        self.db.flush()
        return True

    def has_children(self, category_id: int) -> bool:
        return (
            self.db.scalar(
                select(func.count()).where(TicketCategory.parent_id == category_id)
            )
            or 0
        ) > 0

    def has_tickets(self, category_id: int) -> bool:
        return (
            self.db.scalar(select(func.count()).where(Ticket.category_id == category_id))
            or 0
        ) > 0

    def ensure_enabled_category(self, category_id: int) -> TicketCategory:
        category = self.get(category_id)
        if category is None or category.status != 1:
            raise TicketCategoryNotFoundError
        return category

    def _validate_unique_code(self, code: str, *, exclude_id: int | None = None) -> None:
        stmt = select(TicketCategory).where(TicketCategory.code == code)
        if exclude_id is not None:
            stmt = stmt.where(TicketCategory.id != exclude_id)
        if self.db.scalar(stmt) is not None:
            raise TicketCategoryConflictError("工单分类编码已存在")

    def _validate_parent(self, category_id: int, parent_id: int | None) -> None:
        if parent_id is None:
            return
        if parent_id == category_id:
            raise TicketCategoryValidationError("不允许把自己设置为父级分类")
        parent = self.get(parent_id)
        if parent is None:
            raise TicketCategoryNotFoundError
        while parent is not None:
            if parent.parent_id == category_id:
                raise TicketCategoryValidationError("不允许形成循环父子关系")
            parent = self.get(parent.parent_id) if parent.parent_id is not None else None

    def _validate_refs(self, data: dict) -> None:
        parent_id = data.get("parent_id")
        if parent_id is not None and self.get(parent_id) is None:
            raise TicketCategoryNotFoundError
        group_id = data.get("default_group_id")
        if group_id is not None:
            group = self.db.get(WorkGroup, group_id)
            if group is None or group.status != 1:
                raise TicketCategoryValidationError("默认运维组不存在或未启用")
        fixed_assignee_id = data.get("fixed_assignee_id")
        if fixed_assignee_id is not None:
            user = self.db.get(User, fixed_assignee_id)
            if user is None or user.status != 1:
                raise TicketCategoryValidationError("固定处理人不存在或未启用")
        strategy = data.get("assignment_strategy")
        if strategy == "fixed_user" and fixed_assignee_id is None:
            raise TicketCategoryValidationError("fixed_user 策略必须配置 fixed_assignee_id")
        if strategy == "least_workload" and group_id is None:
            raise TicketCategoryValidationError("least_workload 策略必须配置 default_group_id")
