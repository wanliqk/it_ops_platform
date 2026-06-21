from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetCategory
from app.schemas.asset import AssetCategoryCreate, AssetCreate


class AssetService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: AssetCreate) -> Asset:
        asset = Asset(**payload.model_dump())
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def list(self) -> list[Asset]:
        return list(self.db.scalars(select(Asset).order_by(Asset.id.desc())))


class AssetCategoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: AssetCategoryCreate) -> AssetCategory:
        category = AssetCategory(**payload.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def list(self) -> list[AssetCategory]:
        return list(self.db.scalars(select(AssetCategory).order_by(AssetCategory.id.asc())))
