from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.v1.deps import DBSession, require_permissions
from app.core.responses import APIException, success
from app.models import TicketAssignmentRule, User
from app.schemas.common import page_data
from app.schemas.ticket_assignment_schema import (
    TicketAssignmentRuleCreate,
    TicketAssignmentRuleStatusUpdate,
    TicketAssignmentRuleUpdate,
)
from app.services.log_service import LogService
from app.services.ticket_assignment_service import (
    TicketAssignmentService,
    TicketAssignmentValidationError,
)

router = APIRouter()
RuleReader = Annotated[User, Depends(require_permissions("ticket:assignment-rule:list"))]
RuleCreator = Annotated[User, Depends(require_permissions("ticket:assignment-rule:create"))]
RuleUpdater = Annotated[User, Depends(require_permissions("ticket:assignment-rule:update"))]
RuleStatusUpdater = Annotated[User, Depends(require_permissions("ticket:assignment-rule:status"))]
RuleDeleter = Annotated[User, Depends(require_permissions("ticket:assignment-rule:delete"))]


def assignment_rule_dict(rule: TicketAssignmentRule) -> dict:
    return {
        "id": rule.id,
        "name": rule.name,
        "category_id": rule.category_id,
        "priority": rule.priority,
        "ops_group_id": rule.ops_group_id,
        "ops_group_name": rule.ops_group.group_name if rule.ops_group else None,
        "assign_strategy": rule.assign_strategy,
        "target_user_id": rule.target_user_id,
        "target_user_name": rule.target_user.real_name if rule.target_user else None,
        "enabled": bool(rule.enabled),
        "sort_order": rule.sort_order,
        "remark": rule.remark,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
    }


@router.get("")
def list_assignment_rules(
    db: DBSession,
    _: RuleReader,
    name: str | None = None,
    category_id: int | None = None,
    priority: str | None = None,
    ops_group_id: int | None = None,
    target_user_id: int | None = None,
    assign_strategy: str | None = None,
    enabled: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict:
    items, total = TicketAssignmentService(db).list_rules(
        name=name,
        category_id=category_id,
        priority=priority,
        ops_group_id=ops_group_id,
        target_user_id=target_user_id,
        assign_strategy=assign_strategy,
        enabled=enabled,
        page=page,
        page_size=page_size,
    )
    return success(
        page_data([assignment_rule_dict(item) for item in items], total, page, page_size)
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_assignment_rule(
    payload: TicketAssignmentRuleCreate,
    db: DBSession,
    request: Request,
    current_user: RuleCreator,
) -> dict:
    try:
        rule = TicketAssignmentService(db).create_rule(payload)
    except TicketAssignmentValidationError as exc:
        raise APIException(str(exc), status.HTTP_400_BAD_REQUEST, 40000) from exc
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单自动分配规则",
        operation_type="create",
        business_id=rule.id,
        request=request,
    )
    db.commit()
    return success(assignment_rule_dict(rule), "自动分配规则创建成功")


@router.put("/{rule_id}")
def update_assignment_rule(
    rule_id: int,
    payload: TicketAssignmentRuleUpdate,
    db: DBSession,
    request: Request,
    current_user: RuleUpdater,
) -> dict:
    try:
        rule = TicketAssignmentService(db).update_rule(rule_id, payload)
    except TicketAssignmentValidationError as exc:
        raise APIException(str(exc), status.HTTP_400_BAD_REQUEST, 40000) from exc
    if rule is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单自动分配规则",
        operation_type="update",
        business_id=rule_id,
        request=request,
    )
    db.commit()
    return success(assignment_rule_dict(rule), "自动分配规则修改成功")


@router.patch("/{rule_id}/status")
def update_assignment_rule_status(
    rule_id: int,
    payload: TicketAssignmentRuleStatusUpdate,
    db: DBSession,
    request: Request,
    current_user: RuleStatusUpdater,
) -> dict:
    rule = TicketAssignmentService(db).update_rule_status(rule_id, payload.enabled)
    if rule is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单自动分配规则",
        operation_type="update_status",
        business_id=rule_id,
        request=request,
    )
    db.commit()
    return success(assignment_rule_dict(rule), "自动分配规则状态修改成功")


@router.delete("/{rule_id}")
def delete_assignment_rule(
    rule_id: int,
    db: DBSession,
    request: Request,
    current_user: RuleDeleter,
) -> dict:
    deleted = TicketAssignmentService(db).delete_rule(rule_id)
    if not deleted:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单自动分配规则",
        operation_type="delete",
        business_id=rule_id,
        request=request,
    )
    db.commit()
    return success(None, "自动分配规则删除成功")
