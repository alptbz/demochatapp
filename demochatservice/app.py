import os
from datetime import datetime, timedelta, timezone
from http.client import HTTPException

import jwt
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
from werkzeug.security import check_password_hash

import helper
import models
import testdata
from auth_middleware import token_required
from models import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a SECRET'
app.config['SECRET_KEY'] = SECRET_KEY

db.init_app(app)

with app.app_context():
    db.create_all()

app.app_context().push()

testdata.insert_test_data_if_none(db)


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e

    return {
            "error": "Something went wrong",
            "message": str(e)
        }, 500


@app.route('/conversations')
@token_required
def get_conversations(current_user):
    all_usernames = [x[0] for x in list(db.session.execute(db.Select(models.User.username)).all())]
    all_usernames.remove(current_user.username)
    return jsonify(all_usernames)


@app.route('/conversation/<other>')
@token_required
def get_conversation(current_user, other):
    messages = db.session.execute(db.Select(models.ChatMessage).where(or_(
                        and_(models.ChatMessage.receiver == other, models.ChatMessage.sender == current_user.username),
                        and_(models.ChatMessage.sender == other, models.ChatMessage.receiver == current_user.username)))).all()
    return helper.to_json(messages)


@app.route('/conversations/updates/<int:id>')
@token_required
def get_conversations_updates(current_user, id):
    messages = db.session.execute(db.Select(models.ChatMessage).where(
        and_(models.ChatMessage.id > id,
             or_(models.ChatMessage.receiver == current_user.username, models.ChatMessage.sender == current_user.username)))).all()
    return helper.to_json(messages)


@app.route("/send", methods=["POST"])
@token_required
def send_message(current_user):
    data = request.json
    if not data:
        return {
            "message": "No message content",
            "data": None,
            "error": "Bad request"
        }, 400
    user = db.session.execute(db.Select(models.User).where(models.User.username == data["to"])).one_or_none()
    if user is None:
        return {
            "message": "invalid receiver (to)",
            "data": None,
            "error": "Bad request"
        }, 400
    cm = models.ChatMessage(datetime.now(), current_user.username, data["to"], data["message"])
    db.session.add(cm)
    db.session.commit()

    return {"message": "sent", "data":None}


def validate_username_and_password(username, password):
    user = db.session.execute(db.Select(models.User).where(models.User.username == username)).one_or_none()
    if user != None:
        user = user[0]
        if not check_password_hash(user.password, password):
            return None
    return user


@app.route("/users/login", methods=["POST"])
def login():
    try:
        data = request.json
        if not data:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400
        # validate input
        user = validate_username_and_password(data.get('username'), data.get('password'))
        if user is None:
            return {
                "message": "Error fetching auth token!, invalid username or password",
                "data": None,
                "error": "Unauthorized"
            }, 404
        user = user.to_dict()
        try:
            user["token"] = jwt.encode(
                {'exp': datetime.now(tz=timezone.utc)+timedelta(minutes=60), "user_id": user["id"]},
                app.config["SECRET_KEY"],
                algorithm="HS256",
            )
            del user["password"]
            return {
                "message": "Successfully fetched auth token",
                "data": user
            }
        except Exception as e:
            return {
                "error": "Something went wrong",
                "message": str(e)
            }, 500
    except Exception as e:
        return {
                "message": "Something went wrong!",
                "error": str(e),
                "data": None
        }, 500


if __name__ == '__main__':
    app.run()
