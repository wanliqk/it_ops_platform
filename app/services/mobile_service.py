from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.responses import MobileAPIException
from app.models import (
    Asset,
    AssetStatus,
    Faq,
    FaqCategory,
    Ticket,
    TicketAction,
    TicketRecord,
    TicketStatus,
    User,
)
from app.schemas.mobile import MobileTicketCreate
from app.schemas.ticket import TicketCreate
from app.services.ticket_category_service import TicketCategoryNotFoundError
from app.services.ticket_service import TicketCategoryRequiredError, TicketService


class MobileTicketService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def summary(self, user: User) -> dict[str, int]:
        rows = self.db.execute(
            select(Ticket.status, func.count(Ticket.id))
            .where(Ticket.reporter_id == user.id)
            .group_by(Ticket.status)
        ).all()
        counts = {str(status): count for status, count in rows}
        return {
            "total_count": sum(counts.values()),
            "pending_count": counts.get(TicketStatus.PENDING_ACCEPT.value, 0)
            + counts.get(TicketStatus.PENDING.value, 0),
            "assigned_count": counts.get(TicketStatus.ASSIGNED.value, 0),
            "processing_count": counts.get(TicketStatus.PROCESSING.value, 0),
            "completed_count": counts.get(TicketStatus.COMPLETED.value, 0),
            "cancelled_count": counts.get(TicketStatus.CANCELLED.value, 0),
        }

    def recent(self, user: User, limit: int) -> list[Ticket]:
        return list(
            self.db.scalars(
                select(Ticket)
                .where(Ticket.reporter_id == user.id)
                .order_by(Ticket.created_at.desc())
                .limit(limit)
            )
        )

    def list(
        self,
        user: User,
        page: int,
        page_size: int,
        status: TicketStatus | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Ticket], int]:
        conditions = [Ticket.reporter_id == user.id]
        if status is not None:
            conditions.append(Ticket.status == status)
        if keyword:
            pattern = f"%{keyword}%"
            conditions.append(or_(Ticket.ticket_no.like(pattern), Ticket.title.like(pattern)))

        total = self.db.scalar(select(func.count(Ticket.id)).where(*conditions)) or 0
        items = list(
            self.db.scalars(
                select(Ticket)
                .where(*conditions)
                .order_by(Ticket.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total

    def create(self, user: User, payload: MobileTicketCreate) -> Ticket:
        if payload.asset_id is not None:
            asset = self.db.get(Asset, payload.asset_id)
            if asset is None or asset.status == AssetStatus.SCRAPPED:
                raise MobileAPIException("资产不存在或已报废")
        try:
            return TicketService(self.db).create(
                TicketCreate(
                    title=payload.title,
                    description=payload.description,
                    category_id=payload.category_id,
                    priority=payload.priority,
                    reporter_id=user.id,
                    asset_id=payload.asset_id,
                )
            )
        except TicketCategoryNotFoundError as exc:
            raise MobileAPIException("工单分类不存在或未启用") from exc
        except TicketCategoryRequiredError as exc:
            raise MobileAPIException("该工单分类要求关联资产") from exc

    def detail(self, user: User, ticket_id: int) -> Ticket:
        ticket = self.db.scalar(
            select(Ticket)
            .options(
                selectinload(Ticket.reporter),
                selectinload(Ticket.handler),
                selectinload(Ticket.category),
                selectinload(Ticket.asset),
                selectinload(Ticket.repair_records),
                selectinload(Ticket.records).selectinload(TicketRecord.operator),
            )
            .where(Ticket.id == ticket_id)
        )
        if ticket is None:
            raise MobileAPIException("工单不存在", status_code=404)
        if ticket.reporter_id != user.id:
            raise MobileAPIException("无权查看该工单", status_code=403)
        ticket.records.sort(key=lambda record: record.created_at)
        return ticket

    def cancel(self, user: User, ticket_id: int, reason: str) -> Ticket:
        ticket = self.db.get(Ticket, ticket_id)
        if ticket is None:
            raise MobileAPIException("工单不存在", status_code=404)
        if ticket.reporter_id != user.id:
            raise MobileAPIException("无权取消该工单", status_code=403)
        if ticket.status not in {TicketStatus.PENDING_ACCEPT, TicketStatus.PENDING}:
            raise MobileAPIException("只有待处理状态的工单可以取消")

        ticket.status = TicketStatus.CANCELLED
        self.db.add(
            TicketRecord(
                ticket_id=ticket.id,
                operator_id=user.id,
                from_status=ticket.status,
                to_status=TicketStatus.CANCELLED,
                action=TicketAction.CANCEL,
                remark=reason,
            )
        )
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def _generate_ticket_no(self) -> str:
        prefix = f"TK{datetime.now().strftime('%Y%m%d')}"
        latest_no = self.db.scalar(
            select(func.max(Ticket.ticket_no)).where(Ticket.ticket_no.like(f"{prefix}%"))
        )
        sequence = int(latest_no[-4:]) + 1 if latest_no else 1
        return f"{prefix}{sequence:04d}"


class MobileAssetService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def options(self, user: User, keyword: str | None = None) -> list[Asset]:
        conditions = [Asset.user_id == user.id, Asset.status != AssetStatus.SCRAPPED]
        if keyword:
            pattern = f"%{keyword}%"
            conditions.append(
                or_(
                    Asset.asset_no.like(pattern),
                    Asset.asset_name.like(pattern),
                    Asset.brand.like(pattern),
                    Asset.model.like(pattern),
                )
            )
        return list(self.db.scalars(select(Asset).where(*conditions).order_by(Asset.id.desc())))


class MobileFaqService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        page: int,
        page_size: int,
        category: FaqCategory | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Faq], int]:
        conditions = [Faq.status == 1]
        if category is not None:
            conditions.append(Faq.category == category)
        if keyword:
            pattern = f"%{keyword}%"
            conditions.append(or_(Faq.title.like(pattern), Faq.summary.like(pattern)))

        total = self.db.scalar(select(func.count(Faq.id)).where(*conditions)) or 0
        items = list(
            self.db.scalars(
                select(Faq)
                .where(*conditions)
                .order_by(Faq.sort_order.asc(), Faq.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total

    def detail(self, faq_id: int) -> Faq:
        faq = self.db.scalar(select(Faq).where(Faq.id == faq_id, Faq.status == 1))
        if faq is None:
            raise MobileAPIException("FAQ不存在或已停用", status_code=404)
        faq.view_count += 1
        self.db.commit()
        self.db.refresh(faq)
        return faq
