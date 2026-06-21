from fastapi import APIRouter

from app.api.v1.routes import assets, health, tickets, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
