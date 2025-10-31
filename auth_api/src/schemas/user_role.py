from uuid import UUID

from pydantic import BaseModel


class UserRoleCreate(BaseModel):
    user_id: UUID
    role_id: UUID
