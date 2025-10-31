from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from sqlalchemy.orm import relationship
from src.db.base import Base
from src.db.models.role import user_roles_table

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    login_history = relationship(
        "LoginHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Связь с ролями через промежуточную таблицу
    roles = relationship("Role", secondary=user_roles_table, back_populates="users")