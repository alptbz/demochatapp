from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

import models


def insert_test_data_if_none(db: SQLAlchemy):
    cm = db.session.execute(db.Select(models.ChatMessage)).all()
    if len(cm) == 0:
        chatmessages = [
            models.ChatMessage(sender="max", receiver="peter", created=datetime.now(), message="Hallo"),
            models.ChatMessage(sender="peter", receiver="max", created=datetime.now(), message="Hello"),
            models.ChatMessage(sender="max", receiver="philipp", created=datetime.now(), message="Hello"),
            models.ChatMessage(sender="john", receiver="max", created=datetime.now(), message="Hello"),
        ]
        db.session.add_all(chatmessages)
        db.session.commit()

    us = db.session.execute(db.Select(models.User)).all()
    if len(us) == 0:
        users = [
            models.User(username="max", password=generate_password_hash('1234')),
            models.User(username="peter", password=generate_password_hash('1234')),
            models.User(username="philipp", password=generate_password_hash('1234')),
            models.User(username="john", password=generate_password_hash('1234')),
        ]
        db.session.add_all(users)
        db.session.commit()