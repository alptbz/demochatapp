from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash


class Base(DeclarativeBase):
  pass


db = SQLAlchemy(model_class=Base)


class ChatMessage (db.Model, SerializerMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created: Mapped[datetime] = mapped_column(DateTime, unique=False, nullable=False)
    sender: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    receiver: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    message: Mapped[str] = mapped_column(String, unique=False, nullable=False)

    def __init__(self, created, sender, receiver, message):
        self.created = created
        self.sender = sender
        self.receiver = receiver
        self.message = message


class User(db.Model, SerializerMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    password: Mapped[str] = mapped_column(String, unique=False, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
