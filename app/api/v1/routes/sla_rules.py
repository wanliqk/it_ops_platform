from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.v1.deps import DBSession, require_permissions
from app.core.responses import APIException, success
from app.models import User
from app.schemas.common import page_data
from app.schemas.sla_rule_schema import (
    SlaRuleCreate,
    SlaRuleEnabledUpdate,
    SlaRuleRead,
    SlaRuleUpdate,
)
from app.services.log_service import LogService
from app.services.sla_service import SlaService

router = APIRouter()
SlaRuleReader = Annotated[User, Depends(require_permissions("sla:rule:list"))]
SlaRuleCreator = Annotated[User, Depends(require_permissions("sla:rule:create"))]
SlaRuleUpdater = Annotated[User, Depends(require_permissions("sla:rule:update"))]
SlaRuleEnabler = Annotated[User, Depends(require_permissions("sla:rule:enable"))]
SlaRuleDeleter = Annotated[User, Depends(require_permissions("sla:rule:delete"))]


def sla_rule_dict(rule: object) -> dict:
    return SlaRuleRead.model_validate(rule).model_dump()


@router.get("")
def list_sla_rules(
    db: DBSession,
    _: SlaRuleReader,
    priority: str | None = None,
    category_id: int | None = None,
    enabled: Annotated[int | None, Query(ge=0, le=1)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict:
    items, total = SlaService(db).list_rules(
        priority=priority,
        category_id=category_id,
        enabled=enabled,
        page=page,
        page_size=page_size,
    )
    return success(page_data([sla_rule_dict(item) for item in items], total, page, page_size))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_sla_rule(
    payload: SlaRuleCreate,
    db: DBSession,
    request: Request,
    current_user: SlaRuleCreator,
) -> dict:
    rule = SlaService(db).create_rule(payload)
    LogService(db).record(
        user_id=current_user.id,
        module_name="SLA规则",
        operation_type="create",
        business_id=rule.id,
        request=request,
    )
    db.commit()
    return success(sla_rule_dict(rule), "SLA规则创建成功")


@router.put("/{rule_id}")
def update_sla_rule(
    rule_id: int,
    payload: SlaRuleUpdate,
    db: DBSession,
    request: Request,
    current_user: SlaRuleUpdater,
) -> dict:
    try:
        rule = SlaService(db).update_rule(rule_id, payload)
    except ValueError as exc:
        raise APIException(str(exc), status.HTTP_400_BAD_REQUEST, 40000) from exc
    if rule is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="SLA规则",
        operation_type="update",
        business_id=rule_id,
        request=request,
    )
    db.commit()
    return success(sla_rule_dict(rule), "SLA规则修改成功")


@router.patch("/{rule_id}/enabled")
def update_sla_rule_enabled(
    rule_id: int,
    payload: SlaRuleEnabledUpdate,
    db: DBSession,
    request: Request,
    current_user: SlaRuleEnabler,
) -> dict:
    rule = SlaService(db).update_enabled(rule_id, payload.enabled)
    if rule is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="SLA规则",
        operation_type="update_enabled",
        business_id=rule_id,
        request=request,
    )
    db.commit()
    return success(sla_rule_dict(rule), "SLA规则状态修改成功")


@router.delete("/{rule_id}")
def delete_sla_rule(
    rule_id: int,
    db: DBSession,
    request: Request,
    current_user: SlaRuleDeleter,
) -> dict:
    deleted = SlaService(db).delete_rule(rule_id)
    if not deleted:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="SLA规则",
        operation_type="delete",
        business_id=rule_id,
        request=request,
    )
    db.commit()
    return success(None, "SLA规则删除成功")
