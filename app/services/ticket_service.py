from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketAction, TicketRecord, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: TicketCreate) -> Ticket:
        data = payload.model_dump()
        data["ticket_no"] = data["ticket_no"] or self._generate_ticket_no()
        ticket = Ticket(**data)
        self.db.add(ticket)
        self.db.flush()
        self.db.add(
            TicketRecord(
                ticket_id=ticket.id,
                operator_id=ticket.reporter_id,
                from_status=None,
                to_status=TicketStatus.PENDING,
                action=TicketAction.CREATE,
                remark="用户提交报修工单",
            )
        )
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def list(self) -> list[Ticket]:
        return list(self.db.scalars(select(Ticket).order_by(Ticket.created_at.desc())))

    def update(self, ticket_id: int, payload: TicketUpdate) -> Ticket | None:
        ticket = self.db.get(Ticket, ticket_id)
        if ticket is None:
            return None

        before_status = ticket.status
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(ticket, field, value)

        if payload.status is not None and payload.status != before_status:
            self.db.add(
                TicketRecord(
                    ticket_id=ticket.id,
                    operator_id=payload.handler_id or ticket.handler_id or ticket.reporter_id,
                    from_status=before_status,
                    to_status=payload.status,
                    action=self._action_for_status(payload.status),
                    remark="工单状态变更",
                )
            )

        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def _generate_ticket_no(self) -> str:
        today = datetime.now(UTC).strftime("%Y%m%d")
        prefix = f"TK{today}"
        latest_no = self.db.scalar(
            select(func.max(Ticket.ticket_no)).where(Ticket.ticket_no.like(f"{prefix}%"))
        )
        if latest_no:
            sequence = int(latest_no[-4:]) + 1
        else:
            sequence = 1
        return f"{prefix}{sequence:04d}"

    def _action_for_status(self, status: TicketStatus) -> TicketAction:
        actions = {
            TicketStatus.ASSIGNED: TicketAction.ASSIGN,
            TicketStatus.PROCESSING: TicketAction.START,
            TicketStatus.COMPLETED: TicketAction.FINISH,
            TicketStatus.CANCELLED: TicketAction.CANCEL,
        }
        return actions.get(status, TicketAction.CREATE)
