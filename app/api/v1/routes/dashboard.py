from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import DBSession, require_permissions
from app.core.responses import success
from app.models import User
from app.services.dashboard_service import DashboardService

router = APIRouter()
DashboardUser = Annotated[User, Depends(require_permissions("dashboard:view"))]


@router.get("/summary")
def summary(db: DBSession, _: DashboardUser) -> dict:
    return success(DashboardService(db).summary())


@router.get("/ticket-trend")
def ticket_trend(
    db: DBSession,
    _: DashboardUser,
    days: Annotated[int, Query(ge=1, le=30)] = 7,
) -> dict:
    return success(DashboardService(db).ticket_trend(days))


@router.get("/ticket-categories")
def ticket_categories(db: DBSession, _: DashboardUser) -> dict:
    return success(DashboardService(db).ticket_categories())


@router.get("/asset-status")
def asset_status(db: DBSession, _: DashboardUser) -> dict:
    return success(DashboardService(db).asset_status())


@router.get("/handler-ranking")
def handler_ranking(
    db: DBSession,
    _: DashboardUser,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict:
    return success(
        DashboardService(db).handler_ranking(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
    )
