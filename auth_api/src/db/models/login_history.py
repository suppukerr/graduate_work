from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.base import Base
from pydantic import BaseModel

class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    login_time = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="login_history")


class LoginHistoryRead(BaseModel):
    login_time: datetime
    ip_address: str | None = None
    user_agent: str | None = None

    class Config:
        from_attributes = True