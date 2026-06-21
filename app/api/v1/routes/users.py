from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter()
DBSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: DBSession) -> UserRead:
    service = UserService(db)
    if service.get_by_username(payload.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    return service.create(payload)


@router.get("", response_model=list[UserRead])
def list_users(db: DBSession) -> list[UserRead]:
    return UserService(db).list()
