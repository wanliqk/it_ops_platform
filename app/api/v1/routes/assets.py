from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.asset import AssetCategoryCreate, AssetCategoryRead, AssetCreate, AssetRead
from app.services.asset_service import AssetCategoryService, AssetService

router = APIRouter()
DBSession = Annotated[Session, Depends(get_db)]


@router.post("/categories", response_model=AssetCategoryRead, status_code=status.HTTP_201_CREATED)
def create_asset_category(
    payload: AssetCategoryCreate,
    db: DBSession,
) -> AssetCategoryRead:
    return AssetCategoryService(db).create(payload)


@router.get("/categories", response_model=list[AssetCategoryRead])
def list_asset_categories(db: DBSession) -> list[AssetCategoryRead]:
    return AssetCategoryService(db).list()


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: DBSession) -> AssetRead:
    return AssetService(db).create(payload)


@router.get("", response_model=list[AssetRead])
def list_assets(db: DBSession) -> list[AssetRead]:
    return AssetService(db).list()
