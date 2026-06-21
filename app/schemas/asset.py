from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.asset import AssetStatus


class AssetCategoryBase(BaseModel):
    category_name: str
    category_code: str
    description: str | None = None
    status: int = 1


class AssetCategoryCreate(AssetCategoryBase):
    pass


class AssetCategoryRead(AssetCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetBase(BaseModel):
    asset_no: str
    asset_name: str
    category_id: int
    brand: str | None = None
    model: str | None = None
    serial_no: str | None = None
    user_id: int | None = None
    department: str | None = None
    location: str | None = None
    status: AssetStatus = AssetStatus.IN_USE
    purchase_date: date | None = None
    warranty_expire_date: date | None = None
    remark: str | None = None


class AssetCreate(AssetBase):
    pass


class AssetRead(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
