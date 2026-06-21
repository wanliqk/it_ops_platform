from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    real_name: str
    role: UserRole = UserRole.EMPLOYEE
    department: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    status: int = 1


class UserCreate(UserBase):
    password_hash: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
