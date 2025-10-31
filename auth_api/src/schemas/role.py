from pydantic import BaseModel
from uuid import UUID


class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
