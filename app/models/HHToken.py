# app/models/HHToken.py
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.database import Base


class HHToken(Base):
    __tablename__ = "hh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_in = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
