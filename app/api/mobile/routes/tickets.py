from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.mobile.deps import DBSession, get_current_mobile_user
from app.core.responses import success_response
from app.models import TicketCategory, TicketPriority, TicketStatus, User
from app.schemas.mobile import (
    MobileResponse,
    MobileTicketCancelled,
    MobileTicketCancelRequest,
    MobileTicketCreate,
    MobileTicketCreated,
    MobileTicketDetail,
    MobileTicketListItem,
    OptionItem,
    PageData,
    TicketFormOptionsData,
)
from app.services.mobile_service import MobileTicketService

router = APIRouter()
CurrentUser = Annotated[User, Depends(get_current_mobile_user)]


@router.get("/recent", response_model=MobileResponse[list[MobileTicketListItem]])
def recent_tickets(
    current_user: CurrentUser,
    db: DBSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
) -> dict:
    return success_response(MobileTicketService(db).recent(current_user, limit))


@router.get("/form-options", response_model=MobileResponse[TicketFormOptionsData])
def form_options(current_user: CurrentUser, db: DBSession) -> dict:
    _ = current_user
    categories = db.query(TicketCategory).filter(TicketCategory.status == 1).all()
    return success_response(
        TicketFormOptionsData(
            categories=[
                OptionItem(value=str(category.id), label=category.name)
                for category in sorted(categories, key=lambda item: (item.sort_order, item.id))
            ],
            priorities=[
                OptionItem(value=TicketPriority.LOW, label="低"),
                OptionItem(value=TicketPriority.NORMAL, label="普通"),
                OptionItem(value=TicketPriority.HIGH, label="高"),
                OptionItem(value=TicketPriority.URGENT, label="紧急"),
            ],
        )
    )


@router.post("", response_model=MobileResponse[MobileTicketCreated])
def create_ticket(
    payload: MobileTicketCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    ticket = MobileTicketService(db).create(current_user, payload)
    return success_response(ticket)


@router.get("", response_model=MobileResponse[PageData[MobileTicketListItem]])
def list_tickets(
    current_user: CurrentUser,
    db: DBSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    status: Annotated[TicketStatus | None, Query()] = None,
    keyword: Annotated[str | None, Query()] = None,
) -> dict:
    items, total = MobileTicketService(db).list(current_user, page, page_size, status, keyword)
    return success_response(
        PageData[MobileTicketListItem](
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/{ticket_id}", response_model=MobileResponse[MobileTicketDetail])
def ticket_detail(ticket_id: int, current_user: CurrentUser, db: DBSession) -> dict:
    return success_response(MobileTicketService(db).detail(current_user, ticket_id))


@router.post("/{ticket_id}/cancel", response_model=MobileResponse[MobileTicketCancelled])
def cancel_ticket(
    ticket_id: int,
    payload: MobileTicketCancelRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    return success_response(MobileTicketService(db).cancel(current_user, ticket_id, payload.reason))
