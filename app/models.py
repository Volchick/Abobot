# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

user_roles = Table(
    "user_roles", Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True)
)

dialog_users = Table(
    "dialog_users", Base.metadata,
    Column("dialog_id", ForeignKey("dialogs.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    dialogs = relationship("Dialog", secondary=dialog_users, back_populates="users")
    messages = relationship("Message", back_populates="sender")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship("User", secondary=user_roles, back_populates="roles")

class Dialog(Base):
    __tablename__ = "dialogs"
    id = Column(Integer, primary_key=True)
    users = relationship("User", secondary=dialog_users, back_populates="dialogs")
    messages = relationship("Message", back_populates="dialog")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    dialog_id = Column(Integer, ForeignKey("dialogs.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    dialog = relationship("Dialog", back_populates="messages")
    sender = relationship("User", back_populates="messages")