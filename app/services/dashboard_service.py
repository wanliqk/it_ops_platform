from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Asset, Ticket, TicketCategory, TicketStatus, User

ASSET_STATUS_NAMES = {
    "in_use": "在用",
    "idle": "闲置",
    "repairing": "维修中",
    "scrapped": "已报废",
}


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def summary(self) -> dict[str, int]:
        return {
            "ticket_total": self.db.scalar(select(func.count()).select_from(Ticket)) or 0,
            "ticket_pending": self._ticket_count("pending"),
            "ticket_processing": self._ticket_count("processing"),
            "ticket_completed": self._ticket_count("completed"),
            "asset_total": self.db.scalar(select(func.count()).select_from(Asset)) or 0,
            "asset_in_use": self._asset_count("in_use"),
            "asset_repairing": self._asset_count("repairing"),
            "asset_scrapped": self._asset_count("scrapped"),
        }

    def ticket_trend(self, days: int = 7) -> list[dict[str, int | str]]:
        days = min(max(days, 1), 30)
        today = datetime.now(UTC).date()
        start = today - timedelta(days=days - 1)
        rows = self.db.execute(
            select(func.date(Ticket.created_at), func.count(Ticket.id))
            .where(Ticket.created_at >= datetime.combine(start, datetime.min.time()))
            .group_by(func.date(Ticket.created_at))
        ).all()
        counts = {str(row[0]): row[1] for row in rows}
        return [
            {
                "date": str(start + timedelta(days=offset)),
                "count": counts.get(str(start + timedelta(days=offset)), 0),
            }
            for offset in range(days)
        ]

    def ticket_categories(self) -> list[dict[str, int | str]]:
        rows = self.db.execute(
            select(
                Ticket.category_id,
                TicketCategory.name,
                TicketCategory.code,
                func.count(Ticket.id),
            )
            .join(TicketCategory, TicketCategory.id == Ticket.category_id)
            .group_by(Ticket.category_id, TicketCategory.name, TicketCategory.code)
        ).all()
        return [
            {
                "category_id": category_id,
                "category_name": name,
                "category_code": code,
                "count": count,
            }
            for category_id, name, code, count in rows
        ]

    def asset_status(self) -> list[dict[str, int | str]]:
        rows = self.db.execute(
            select(Asset.status, func.count(Asset.id)).group_by(Asset.status)
        ).all()
        return [
            {
                "status": str(asset_status),
                "status_name": ASSET_STATUS_NAMES.get(str(asset_status), str(asset_status)),
                "count": count,
            }
            for asset_status, count in rows
        ]

    def handler_ranking(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 10,
    ) -> list[dict[str, int | str]]:
        stmt = (
            select(Ticket.handler_id, User.real_name, func.count(Ticket.id))
            .join(User, User.id == Ticket.handler_id)
            .where(Ticket.status == TicketStatus.COMPLETED)
            .group_by(Ticket.handler_id, User.real_name)
            .order_by(func.count(Ticket.id).desc())
            .limit(max(1, min(limit, 100)))
        )
        if start_date:
            stmt = stmt.where(
                Ticket.completed_at >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date:
            stmt = stmt.where(
                Ticket.completed_at <= datetime.combine(end_date, datetime.max.time())
            )
        return [
            {"handler_id": handler_id, "handler_name": real_name, "completed_count": count}
            for handler_id, real_name, count in self.db.execute(stmt).all()
        ]

    def _ticket_count(self, status: str) -> int:
        return (
            self.db.scalar(select(func.count()).select_from(Ticket).where(Ticket.status == status))
            or 0
        )

    def _asset_count(self, status: str) -> int:
        return (
            self.db.scalar(select(func.count()).select_from(Asset).where(Asset.status == status))
            or 0
        )
