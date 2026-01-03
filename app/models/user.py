from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, BigInteger, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    active_resume_id = Column(String, nullable=True)

    tokens = relationship("HHToken", back_populates="user")


class TelegramUser(User):
    __tablename__ = "telegram_users"

    # Primary key и foreign key к users.id
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    telegram_username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'telegram_user',
    }


class UserAuth(Base):
    __tablename__ = "users_auth"
    id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    password_hash = Column(String, nullable=False)
    user = relationship("User", backref="auth", uselist=False)
