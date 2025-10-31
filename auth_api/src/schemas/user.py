from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    username: str
    email: EmailStr


class UserResponse(BaseModel):
    id: UUID
    username: str | None = None
    email: EmailStr
    is_superuser: bool = False
    is_active: bool = True

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class ChangeCredentialsRequest(BaseModel):
    new_email: str | None = None
    new_password: str | None = None


class LogoutResponse(BaseModel):
    detail: str
