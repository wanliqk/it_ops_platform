from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.v1.deps import DBSession, require_permissions
from app.api.v1.routes._serializers import ticket_category_dict
from app.core.responses import APIException, success
from app.models import User
from app.schemas.ticket_category_schema import (
    TicketCategoryCreate,
    TicketCategoryStatusUpdate,
    TicketCategoryUpdate,
)
from app.services.log_service import LogService
from app.services.ticket_category_service import (
    TicketCategoryConflictError,
    TicketCategoryNotFoundError,
    TicketCategoryService,
    TicketCategoryValidationError,
)

router = APIRouter()
CategoryReader = Annotated[User, Depends(require_permissions("ticket_category:list"))]
CategoryCreator = Annotated[User, Depends(require_permissions("ticket_category:create"))]
CategoryUpdater = Annotated[User, Depends(require_permissions("ticket_category:update"))]
CategoryDeleter = Annotated[User, Depends(require_permissions("ticket_category:delete"))]
CategoryStatusUpdater = Annotated[User, Depends(require_permissions("ticket_category:status"))]


@router.get("")
def list_ticket_categories(
    db: DBSession,
    _: CategoryReader,
    keyword: str | None = None,
    status_value: Annotated[int | None, Query(alias="status", ge=0, le=1)] = None,
    parent_id: int | None = None,
) -> dict:
    items = TicketCategoryService(db).list_categories(
        keyword=keyword,
        status=status_value,
        parent_id=parent_id,
    )
    return success([ticket_category_dict(item) for item in items])


@router.get("/tree")
def ticket_category_tree(
    db: DBSession,
    _: CategoryReader,
    status_value: Annotated[int | None, Query(alias="status", ge=0, le=1)] = 1,
) -> dict:
    items = TicketCategoryService(db).tree(status=status_value)
    return success([ticket_category_dict(item) for item in items])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_ticket_category(
    payload: TicketCategoryCreate,
    db: DBSession,
    request: Request,
    current_user: CategoryCreator,
) -> dict:
    service = TicketCategoryService(db)
    try:
        category = service.create(payload)
    except TicketCategoryConflictError as exc:
        raise APIException(str(exc), status.HTTP_409_CONFLICT, 40900) from exc
    except (TicketCategoryNotFoundError, TicketCategoryValidationError) as exc:
        raise APIException(str(exc) or "参数错误", status.HTTP_400_BAD_REQUEST, 40000) from exc
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单分类",
        operation_type="create",
        business_id=category.id,
        request=request,
    )
    db.commit()
    return success(ticket_category_dict(category), "工单分类创建成功")


@router.get("/{category_id}")
def get_ticket_category(category_id: int, db: DBSession, _: CategoryReader) -> dict:
    category = TicketCategoryService(db).get(category_id)
    if category is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    return success(ticket_category_dict(category))


@router.put("/{category_id}")
def update_ticket_category(
    category_id: int,
    payload: TicketCategoryUpdate,
    db: DBSession,
    request: Request,
    current_user: CategoryUpdater,
) -> dict:
    service = TicketCategoryService(db)
    try:
        category = service.update(category_id, payload)
    except TicketCategoryConflictError as exc:
        raise APIException(str(exc), status.HTTP_409_CONFLICT, 40900) from exc
    except TicketCategoryNotFoundError as exc:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400) from exc
    except TicketCategoryValidationError as exc:
        raise APIException(str(exc), status.HTTP_400_BAD_REQUEST, 40000) from exc
    if category is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单分类",
        operation_type="update",
        business_id=category_id,
        request=request,
    )
    db.commit()
    return success(ticket_category_dict(category), "工单分类修改成功")


@router.patch("/{category_id}/status")
def update_ticket_category_status(
    category_id: int,
    payload: TicketCategoryStatusUpdate,
    db: DBSession,
    request: Request,
    current_user: CategoryStatusUpdater,
) -> dict:
    category = TicketCategoryService(db).update_status(category_id, payload.status)
    if category is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单分类",
        operation_type="update_status",
        business_id=category_id,
        request=request,
    )
    db.commit()
    return success(ticket_category_dict(category), "工单分类状态修改成功")


@router.delete("/{category_id}")
def delete_ticket_category(
    category_id: int,
    db: DBSession,
    request: Request,
    current_user: CategoryDeleter,
) -> dict:
    try:
        deleted = TicketCategoryService(db).delete(category_id)
    except TicketCategoryConflictError as exc:
        raise APIException(str(exc), status.HTTP_409_CONFLICT, 40900) from exc
    if not deleted:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单分类",
        operation_type="delete",
        business_id=category_id,
        request=request,
    )
    db.commit()
    return success(None, "工单分类停用成功")
