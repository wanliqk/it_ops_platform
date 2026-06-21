from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate
from app.services.ticket_service import TicketService

router = APIRouter()
DBSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate, db: DBSession) -> TicketRead:
    return TicketService(db).create(payload)


@router.get("", response_model=list[TicketRead])
def list_tickets(db: DBSession) -> list[TicketRead]:
    return TicketService(db).list()


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: DBSession,
) -> TicketRead:
    service = TicketService(db)
    ticket = service.update(ticket_id, payload)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket
