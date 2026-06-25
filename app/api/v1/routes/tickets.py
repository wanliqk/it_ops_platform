from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.v1.deps import DBSession, require_permissions
from app.api.v1.routes._serializers import ticket_dict, ticket_record_dict
from app.core.responses import APIException, success
from app.models import User
from app.schemas.common import page_data
from app.schemas.ticket import (
    TicketAssign,
    TicketCancel,
    TicketComplete,
    TicketCreate,
    TicketStart,
    TicketUpdate,
)
from app.services.log_service import LogService
from app.services.ticket_assignment_service import TicketAssignmentService
from app.services.ticket_category_service import TicketCategoryNotFoundError
from app.services.ticket_service import (
    TicketCategoryRequiredError,
    TicketConflictError,
    TicketService,
)
from app.utils.permissions import get_user_role_codes

router = APIRouter()
TicketReader = Annotated[
    User,
    Depends(require_permissions("ticket:view_all", "ticket:view_self", require_all=False)),
]
TicketCreator = Annotated[User, Depends(require_permissions("ticket:create"))]
TicketUpdater = Annotated[User, Depends(require_permissions("ticket:update"))]
TicketAssigner = Annotated[User, Depends(require_permissions("ticket:assign"))]
TicketStarter = Annotated[User, Depends(require_permissions("ticket:start"))]
TicketCompleter = Annotated[User, Depends(require_permissions("ticket:complete"))]
TicketCanceller = Annotated[User, Depends(require_permissions("ticket:cancel"))]
TicketDeleter = Annotated[User, Depends(require_permissions("ticket:delete"))]
TicketRecordReader = Annotated[User, Depends(require_permissions("ticket:records"))]
TicketAutoAssigner = Annotated[User, Depends(require_permissions("ticket:auto-assign"))]


@router.get("")
def list_tickets(
    db: DBSession,
    current_user: TicketReader,
    keyword: str | None = None,
    status_value: Annotated[str | None, Query(alias="status")] = None,
    category_id: int | None = None,
    priority: str | None = None,
    reporter_id: int | None = None,
    handler_id: int | None = None,
    asset_id: int | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict:
    items, total = TicketService(db).list(
        current_user=current_user,
        keyword=keyword,
        status=status_value,
        category_id=category_id,
        priority=priority,
        reporter_id=reporter_id,
        handler_id=handler_id,
        asset_id=asset_id,
        page=page,
        page_size=page_size,
    )
    return success(page_data([ticket_dict(item) for item in items], total, page, page_size))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: DBSession,
    request: Request,
    current_user: TicketCreator,
) -> dict:
    if "admin" not in get_user_role_codes(db, current_user.id) or payload.reporter_id is None:
        payload.reporter_id = current_user.id
    try:
        ticket = TicketService(db).create(payload)
    except TicketCategoryNotFoundError as exc:
        raise APIException("工单分类不存在或未启用", status.HTTP_400_BAD_REQUEST, 40000) from exc
    except TicketCategoryRequiredError as exc:
        raise APIException("该工单分类要求关联资产", status.HTTP_400_BAD_REQUEST, 40000) from exc
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单管理",
        operation_type="create",
        business_id=ticket.id,
        request=request,
    )
    db.commit()
    return success(ticket_dict(ticket), "工单创建成功")


@router.post("/{ticket_id}/auto-assign")
def auto_assign_ticket(
    ticket_id: int,
    db: DBSession,
    request: Request,
    current_user: TicketAutoAssigner,
    force: bool = False,
) -> dict:
    ticket = TicketService(db).get(ticket_id)
    if ticket is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    service = TicketAssignmentService(db)
    result = service.auto_assign_ticket(
        ticket,
        force=force,
        mutate_on_failure=ticket.handler_id is None,
        preserve_existing_on_failure=True,
    )
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单自动分配",
        operation_type="auto_assign",
        business_id=ticket_id,
        request=request,
        operation_result="success" if result.success else "fail",
        error_message=result.fail_reason,
    )
    db.commit()
    return success(service.result_dict(ticket, result))


@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, db: DBSession, current_user: TicketReader) -> dict:
    service = TicketService(db)
    ticket = service.get(ticket_id)
    if ticket is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    if not service.can_access(ticket, current_user):
        raise APIException("无权限操作", status.HTTP_403_FORBIDDEN, 40300)
    return success(ticket_dict(ticket))


@router.put("/{ticket_id}")
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: DBSession,
    request: Request,
    current_user: TicketUpdater,
) -> dict:
    service = TicketService(db)
    ticket = service.get(ticket_id)
    if ticket is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    if not service.can_update(ticket, current_user):
        raise APIException("当前工单状态不允许执行该操作", status.HTTP_409_CONFLICT, 40900)
    try:
        updated = service.update(ticket_id, payload)
    except TicketCategoryNotFoundError as exc:
        raise APIException("工单分类不存在或未启用", status.HTTP_400_BAD_REQUEST, 40000) from exc
    except TicketCategoryRequiredError as exc:
        raise APIException("该工单分类要求关联资产", status.HTTP_400_BAD_REQUEST, 40000) from exc
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单管理",
        operation_type="update",
        business_id=ticket_id,
        request=request,
    )
    db.commit()
    return success(ticket_dict(updated), "工单修改成功")


@router.patch("/{ticket_id}/assign")
def assign_ticket(
    ticket_id: int,
    payload: TicketAssign,
    db: DBSession,
    request: Request,
    current_user: TicketAssigner,
) -> dict:
    try:
        ticket = TicketService(db).assign(ticket_id, payload, current_user.id)
    except TicketConflictError as exc:
        raise APIException("当前工单状态不允许执行该操作", status.HTTP_409_CONFLICT, 40900) from exc
    if ticket is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单管理",
        operation_type="assign",
        business_id=ticket_id,
        request=request,
    )
    db.commit()
    return success(
        {"id": ticket.id, "status": ticket.status, "handler_id": ticket.handler_id},
        "工单已派单",
    )


@router.patch("/{ticket_id}/start")
def start_ticket(
    ticket_id: int,
    payload: TicketStart,
    db: DBSession,
    request: Request,
    current_user: TicketStarter,
) -> dict:
    try:
        ticket = TicketService(db).start(ticket_id, payload, current_user)
    except PermissionError as exc:
        raise APIException("无权限操作", status.HTTP_403_FORBIDDEN, 40300) from exc
    except TicketConflictError as exc:
        raise APIException("当前工单状态不允许执行该操作", status.HTTP_409_CONFLICT, 40900) from exc
    if ticket is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单管理",
        operation_type="start",
        business_id=ticket_id,
        request=request,
    )
    db.commit()
    return success(
        {"id": ticket.id, "status": ticket.status, "started_at": ticket.started_at},
        "工单已开始处理",
    )


@router.patch("/{ticket_id}/complete")
def complete_ticket(
    ticket_id: int,
    payload: TicketComplete,
    db: DBSession,
    request: Request,
    current_user: TicketCompleter,
) -> dict:
    try:
        ticket = TicketService(db).complete(ticket_id, payload, current_user)
    except PermissionError as exc:
        raise APIException("无权限操作", status.HTTP_403_FORBIDDEN, 40300) from exc
    except (TicketConflictError, ValueError) as exc:
        raise APIException("当前工单状态不允许执行该操作", status.HTTP_409_CONFLICT, 40900) from exc
    if ticket is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单管理",
        operation_type="complete",
        business_id=ticket_id,
        request=request,
    )
    db.commit()
    return success(
        {"id": ticket.id, "status": ticket.status, "completed_at": ticket.completed_at},
        "工单已完成",
    )


@router.patch("/{ticket_id}/cancel")
def cancel_ticket(
    ticket_id: int,
    payload: TicketCancel,
    db: DBSession,
    request: Request,
    current_user: TicketCanceller,
) -> dict:
    try:
        ticket = TicketService(db).cancel(ticket_id, payload, current_user)
    except PermissionError as exc:
        raise APIException("无权限操作", status.HTTP_403_FORBIDDEN, 40300) from exc
    except TicketConflictError as exc:
        raise APIException("当前工单状态不允许执行该操作", status.HTTP_409_CONFLICT, 40900) from exc
    if ticket is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单管理",
        operation_type="cancel",
        business_id=ticket_id,
        request=request,
    )
    db.commit()
    return success({"id": ticket.id, "status": ticket.status}, "工单已取消")


@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: DBSession,
    request: Request,
    current_user: TicketDeleter,
) -> dict:
    try:
        deleted = TicketService(db).delete(ticket_id)
    except TicketConflictError as exc:
        raise APIException("当前工单状态不允许执行该操作", status.HTTP_409_CONFLICT, 40900) from exc
    if not deleted:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    LogService(db).record(
        user_id=current_user.id,
        module_name="工单管理",
        operation_type="delete",
        business_id=ticket_id,
        request=request,
    )
    db.commit()
    return success(None, "工单删除成功")


@router.get("/{ticket_id}/records")
def ticket_records(ticket_id: int, db: DBSession, current_user: TicketRecordReader) -> dict:
    service = TicketService(db)
    ticket = service.get(ticket_id)
    if ticket is None:
        raise APIException("资源不存在", status.HTTP_404_NOT_FOUND, 40400)
    if not service.can_access(ticket, current_user):
        raise APIException("无权限操作", status.HTTP_403_FORBIDDEN, 40300)
    return success([ticket_record_dict(record) for record in service.records(ticket_id)])
