from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum, ForeignKey, DateTime, BigInteger
from enum import Enum as PyEnum
from datetime import datetime

from app.database import Base

class UserRole(PyEnum):
    ADMIN = "admin"
    USER = "user"
    # Добавьте другие роли по необходимости

class User(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    vk_code_verifier: Mapped[str] = mapped_column(String, nullable=True)
    vk_access_token: Mapped[str] = mapped_column(String, nullable=True)
    vk_refresh_token: Mapped[str] = mapped_column(String, nullable=True)
    vk_user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    dialog = relationship("Dialog", back_populates="user", uselist=False)

class Dialog(Base):
    __tablename__ = "dialogs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="dialog")
    messages = relationship("Message", back_populates="dialog")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(4096))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    dialog_id: Mapped[int] = mapped_column(ForeignKey("dialogs.id"))

    dialog = relationship("Dialog", back_populates="messages")