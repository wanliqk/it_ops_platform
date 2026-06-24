from fastapi import APIRouter

from app.api.v1.routes import (
    asset_categories,
    assets,
    auth,
    dashboard,
    dicts,
    faqs,
    health,
    notifications,
    operation_logs,
    repair_records,
    sla_rules,
    tickets,
    users,
)
from app.routers import rbac

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(rbac.router, tags=["rbac"])
api_router.include_router(
    asset_categories.router,
    prefix="/asset-categories",
    tags=["asset-categories"],
)
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(faqs.router, prefix="/faqs", tags=["faqs"])
api_router.include_router(repair_records.router, prefix="/repair-records", tags=["repair-records"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(sla_rules.router, prefix="/sla-rules", tags=["sla-rules"])
api_router.include_router(operation_logs.router, prefix="/operation-logs", tags=["operation-logs"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(dicts.router, prefix="/dicts", tags=["dicts"])
