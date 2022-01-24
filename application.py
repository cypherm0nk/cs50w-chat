import os
import time
import uuid
from enum import Enum
from collections import deque
from flask import Flask, session, jsonify, render_template, request, flash, redirect, url_for, make_response
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_session import Session
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)



class MessageType(Enum):
    """ENUM with message types

    Args:
        Enum (MessageType): [Type of message]
    """
    TEXT = 1
    IMAGE = 2
    OTHER = 3


class Message():
    def __init__(self, username, type, text, timestamp, filename):
        self.id = uuid.uuid4().hex
        self.username = username
        self.type = type
        self.text = text
        self.timestamp = timestamp
        self.filename = filename


def is_authenticated():
    """Check if the user is logged in.

    Returns:
        boolean: Returns true if the user is logged in and false if the user is logged out
    """
    username = request.cookies.get('username')
    if not username is None and username:
        if not username in logged_user_list:
            logged_user_list[username] = ""
        return True
    else:
        return False


# list of supported image formats
image_files_list = ["image/bmp", "image/gif",
                    "image/x-icon", "image/jpeg", "image/png", "image/svg+xml"]
# dictionary of channels
channel_list = dict()
# dictionary of logged users
logged_user_list = dict()
LOGIN_TEMPLATE = "login.html"
DATETIME_TEMPLATE = "%m/%d/%Y, %H:%M:%S"


@app.route("/")
def index():
    if not is_authenticated():
        return redirect("/login")
    username = request.cookies.get("username")
    return render_template("index.html", username=username,channel_list=channel_list, logged_user_list=logged_user_list)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template(LOGIN_TEMPLATE)
    elif request.method == 'POST':
        username = request.form.get("username")
        username=username.replace("'","")
        if username in logged_user_list:
            flash("The username already exists!", "danger")
            return render_template(LOGIN_TEMPLATE)
        else:
            logged_user_list[username] = ""
            resp = make_response(redirect("/"))
            resp.set_cookie("username", username,max_age=99999999)
            return resp


@app.route("/logout")
def logout():
    username = request.cookies.get("username")
    resp = make_response(redirect("/login"))
    try:
        resp.delete_cookie("username")
        logged_user_list.pop(username, None)
    except:
        pass
    flash("Logout successful!", "success")
    return resp


@app.route("/createchannel", methods=['GET', 'POST'])
def createchannel():
    if not is_authenticated():
        return redirect("/login")
    username = request.cookies.get('username')
    if request.method == 'GET':
        return render_template("create_channel.html", channel_list=channel_list, logged_user_list=logged_user_list)
    elif request.method == 'POST':
        channel_name = request.form.get('channel_name')
        if channel_name in channel_list:
            flash("The channel name already exists!", "danger")
        else:
            channel_list[channel_name] = deque()
            flash("successfully created channel!", "success")
        return render_template("create_channel.html",username=username, channel_list=channel_list, logged_user_list=logged_user_list)


@app.route("/channel/<string:channelid>", methods=['GET'])
def channel(channelid):
    if not is_authenticated():
        return redirect("/login")
    messages = ""
    try:
        username = request.cookies.get("username")
        logged_user_list[username]=channelid
        messages = channel_list[channelid]
    except:
        channelid = ""
        flash("Channel not found!", "danger")
    return render_template("chat.html", username=username, messages=messages, name=channelid, channel_list=channel_list, logged_user_list=logged_user_list)


@socketio.on("send message")
def send_message(msg):
    username = request.cookies.get("username")
    current_channel=logged_user_list[username]
    message = Message(username, MessageType.TEXT, msg, time.strftime(
        DATETIME_TEMPLATE, time.localtime(time.time())), "")
    messages = channel_list[current_channel]
    if len(messages) > 100:
        messages.popleft()
    messages.append(message)
    channel_list[current_channel] = messages
    emit('return message', {
        'id': message.id,
        'timestamp': message.timestamp,
        'username': username,
        'filename': message.filename,
        'type': message.type.name,
        'is_delete': True,
        'msg': message.text}, room=current_channel)


@socketio.on("send file")
def send(file, name, type):
    username = request.cookies.get("username")
    current_channel=logged_user_list[username]
    type_file = MessageType.OTHER
    if type in image_files_list:
        type_file = MessageType.IMAGE
    message = Message(username, type_file, file, time.strftime(
        DATETIME_TEMPLATE, time.localtime(time.time())), name)
    messages = channel_list[current_channel]
    if len(messages) > 100:
        messages.popleft()
    messages.append(message)

    channel_list[current_channel] = messages
    emit('return message file', {
        'id': message.id,
        'timestamp': message.timestamp,
        'username': username,
        'filename': message.filename,
        'type': message.type.name,
        'is_delete': True,
        'msg': message.text}, room=current_channel)


@socketio.on("delete message")
def delete_message(id):
    username = request.cookies.get("username")
    current_channel=logged_user_list[username]
    messages = channel_list[current_channel]
    for message in messages:
        if message.id == id:
            messages.remove(message)
            break
    channel_list[current_channel] = messages
    emit('return deleted message', {'id': id}, room=current_channel)


@socketio.on("join a room")
def join_a_room():
    username = request.cookies.get("username")
    current_channel=logged_user_list[username]
    logged_user_list[username] = current_channel
    join_room(current_channel)
    emit('room status', {
        'timestamp': time.strftime(DATETIME_TEMPLATE, time.localtime(time.time())),
        'username': username,
        'msg': " joined the channel "+current_channel}, room=current_channel)

@socketio.on("exit a room")
def exit_a_room():
    username = request.cookies.get("username")
    current_channel=logged_user_list[username]
    leave_room(current_channel)
    emit('room status', {
        'timestamp': time.strftime(DATETIME_TEMPLATE, time.localtime(time.time())),
        'username': username,
        'msg': " exit the channel "+current_channel}, room=current_channel)
