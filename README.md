# Project 2 - CHAT
 
## Web Programming with Python and JavaScript

### Harvard University | EDX

- [About Project](#about-project)
- [Requirements](#requirements)
- [Project Files](#project-files)
	- [base-layout](#base_layout)
	- [index](#index)
	- [login](#login)
	- [create_channel](#create_channel)
	- [chat](#chat)
	- [chat_js](#chat_js)
	- [helper_js](#helper_js)
	- [application](#application)


## About Project
This is the documentation of my project2 in which I show in detail the features of my project of book reviews website.
## Requirements
Below I will explain each of the requirements and the files that meet them.
#### Requirement 1
**Display Name**: When a user visits your web application for the first time, they should be prompted to type in a display name that will eventually be associated with every message the user sends. If a user closes the page and returns to your app later, the display name should still be remembered.
#### Requirement 2
**Channel Creation**: Any user should be able to create a new channel, so long as its name doesn’t conflict with the name of an existing channel.
#### Requirement 3
**Channel List**: Users should be able to see a list of all current channels, and selecting one should allow the user to view the channel. We leave it to you to decide how to display such a list.
#### Requirement 4
**Messages View**: Once a channel is selected, the user should see any messages that have already been sent in that channel, up to a maximum of 100 messages. Your app should only store the 100 most recent messages per channel in server-side memory.
#### Requirement 5
**Sending Messages**: Once in a channel, users should be able to send text messages to others the channel. When a user sends a message, their display name and the timestamp of the message should be associated with the message. All users in the channel should then see the new message (with display name and timestamp) appear on their channel page. Sending and receiving messages should NOT require reloading the page.
#### Requirement 6
**Remembering the Channel**: If a user is on a channel page, closes the web browser window, and goes back to your web application, your application should remember what channel the user was on previously and take the user back to that channel.
#### Requirement 7
**Personal Touch**: Add at least one additional feature to your chat application of your choosing! Feel free to be creative, but if you’re looking for ideas, possibilities include: supporting deleting one’s own messages, supporting use attachments (file uploads) as messages, or supporting private messaging between two users.

## Project Files

This project has 10 files that are:
 - static/
   - attach-file.png
   - chat.js
   - helper.js
   - style.css
 - templates/
   - base_layout.html
   - chat.html
   - create_channel.html
   - index.html
   - login.html
  - .flaskenv
  - application.py

###  base_layout
In this file we have the template base where I used the Bootstrap Navbar components in addition to css and javascript.
In addition, the global variables below that take the values of the cookie and localStorage are declared.
````javascript
var  current_username = getCookie("username");
var  last_channel = localStorage.getItem('last_channel');
````
The excerpt below is responsible for listing the groups created according to [Requirement 3](#requirement-3).
````html
 <div class="col-sm-3">
                    <div class="jumbotron jumbotron-fluid">
                        <div class="container">
                            <h4>Channels</h4>
                            <ul class="list-group">
                                {%for channel in channel_list%}
                                <li class="list-group-item"><a
                                        href="{{url_for('channel',channelid=channel)}}">#{{channel}}</a></li>
                                {% endfor %}
                            </ul>
                        </div>
                    </div>
                </div>
 ````
###  index
To satisfy [Requirement 6](#requirement-6),I created the javascript below to retrieve the last channel accessed by the user and direct it to that channel.

````javascript
if (current_username!="") {
	if (last_channel !="" && last_channel!=null) {
	window.location.replace('/channel/' + last_channel);
	}
}
````

### login
This file contains the login form and the javascript below to satisfy requirements  [Requirement 1](#requirement-1) and  [Requirement 6](#requirement-6).
````javascript
if (current_username == "") {
	if (last_channel != "") {
	localStorage.removeItem('last_channel');
	}
}
````
 

### create_channel
In this file is the channel creation form as per  [Requirement 2](#requirement-2).
````html
<div  class="jumbotron">
<form  action="/createchannel"  method="POST"  class="needs-validation"  novalidate>
<div  class="form-group">
<label  for="textChannelName">Channel Name:</label>
<input  type="text"  class="form-control"  name="channel_name"  id="textChannelName"  required>
<div  class="invalid-feedback">
Please provide a channel name!
</div>
</div>
<button  type="submit"  class="btn btn-success my-1">Create Channel</button>
</form>
</div>
````
### chat
This file contains the chat frontend rules.
It has the div #chat_list that contains all the messages sent and received.

### chat_js
This file contains the javascript code that controls the entire chat screen.
In the section below I connect to the socket.
````javascript
var  socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
````
The events below are used to enter and leave a channel at the click of a button.
````javascript
document.querySelector('#btn_join_channel').addEventListener("click", function (event) {
socket.emit('join a room');
$("#txMessage").prop("disabled", false);
$("#file_upload").prop("disabled", false);
localStorage.setItem('last_channel', current_channel)
this.style.visibility = "hidden";
document.querySelector('#btn_exit_channel').style.visibility = "visible";
});
document.querySelector('#btn_exit_channel').addEventListener("click", function (event) {
socket.emit('exit a room');
$("#txMessage").prop("disabled", true);
$("#file_upload").prop("disabled", true);
localStorage.removeItem('last_channel');
this.style.visibility = "hidden";
document.querySelector('#btn_join_channel').style.visibility = "visible";
});
````
To satisfy [Requirement 7](#requirement-7) I created the features below:
This click event is used to delete messages after clicking the X button.
````javascript
document.querySelectorAll("[id^='btn_delete_message_']").forEach(function (button) {
	button.onclick = function () {
	let  id = this.dataset.id;
	socket.emit('delete message', id);
	}
});
````
The event below is used to upload the files by converting them to base64 string and sending through the socket
````javascript
document.querySelector('#file_upload').onchange = function () {
	var  file = this.files[0],
	reader = new  FileReader();
	reader.onloadend = function () {
	var  b64 = reader.result;
	socket.emit('send file', b64, file.name, file.type);
	};
	reader.readAsDataURL(file);
};
````
The sections below are used to receive the return of the sockets.
````javascript
socket.on('return message', data  => {
	sendMessenger(data);
});
socket.on('return message file', data  => {
	sendMessenger(data);
});
socket.on('room status', data  => {
	sendMessenger(data);
});
socket.on('return deleted message', data  => {
	if (data.id != "undefined") {
		document.querySelector('#id_' + data.id).remove();
	}
});
````
The send Messenger function receives the data object and dynamically creates all the html elements that make up the messages according to  [Requirement 4](#requirement-4) and  [Requirement 5](#requirement-5).
````javascript
function  sendMessenger(data) {
let  div_class = "container darker";
let  span_class = "time-left";
let  h3_class = "right";
	if (current_username == data.username) {
		div_class = "container";
		span_class = "time-right";
		h3_class = "";
	}
const  br = document.createElement('BR');
const  div = document.createElement('div');
const  button = document.createElement('BUTTON');
const  span2 = document.createElement('span');
const  h3 = document.createElement('h3');
const  a = document.createElement('A');
var  img = document.createElement("IMG");
const  p = document.createElement('p');
const  span = document.createElement('SPAN');
span.className = span_class;
div.className = div_class;
div.setAttribute("id", "id_" + data.id);
	if (current_username == data.username) {
		button.className = "close delete-button";
		button.setAttribute("data-id", data.id);
		button.setAttribute("id", "btn_delete_message_" + data.id);
		button.setAttribute("type", "submit");
		button.setAttribute("aria-label", "Close");
		button.onclick = function () {
		let  id = this.dataset.id;
		socket.emit('delete message', id);
		};
		span2.setAttribute("aria-hidden", "true");
		span2.innerHTML = "&times";
		button.append(span2);
		div.append(button);
	}
h3.innerHTML = data.username;
h3.className = h3_class;
span.className = "time-right";
span.innerHTML = data.timestamp;
div.append(h3);
a.setAttribute("href", data.msg);
a.setAttribute("target", "_blank");
a.setAttribute("download", data.filename);
	if (data.type == "IMAGE") {
		img.src = data.msg;
		img.width = "250";
		img.className = "img-fluid img-thumbnail";
		a.append(img);
		div.append(a);
		div.append(br);
		p.className = "text-center text-break";
		p.innerHTML = data.filename;
		div.append(p);
		document.querySelector('#file_upload').value = "";
	} 
	else  if (data.type == "OTHER") {
		img.src = file_icon;
		img.width = "250";
		img.className = "img-fluid img-thumbnail";
		a.append(img);
		div.append(a);
		div.append(br);
		p.className = "text-center text-break";
		p.innerHTML = data.filename;
		div.append(p);
		document.querySelector('#file_upload').value = "";
	}
	else {
		p.className = "text-left";
		p.innerHTML = data.msg;
		div.append(p);
	}
div.append(span);
document.querySelector('#chat_list').append(div);
setTimeout(() => {
var  chatList = document.getElementById('chat_list');
chatList.scrollTop = chatList.scrollHeight;
}, 100);
}
````
### helper_js
The getCookie function takes the name of a cookie and returns its result.
````javascript
function  getCookie(cookie_name) {
var  name = cookie_name + "=";
var  decodedCookie = decodeURIComponent(document.cookie);
var  list_cookies = decodedCookie.split(';');
	for(var  i = 0; i <list_cookies.length; i++) {
	var  cookie = list_cookies[i];
		while (cookie.charAt(0) == ' ') {
			cookie = cookie.substring(1);
		}
	if (cookie.indexOf(name) == 0) {
		return  cookie.substring(name.length, cookie.length);
	}
}
return  "";
}
````
### application
In this file are all the backend rules, I will detail them later.

The is_authenticated function checks whether a user is authenticated using cookies.
````python
def  is_authenticated():
	username = request.cookies.get('username')
	if  not username is  None  and username:
		if  not username in logged_user_list:
			logged_user_list[username] = ""
			return  True
	else:
		return  False
````
List of supported image formats:
````python
image_files_list = ["image/bmp", "image/gif",
"image/x-icon", "image/jpeg", "image/png", "image/svg+xml"]
````
Below we have a dictionary containing the groups created and a dictionary for the logged-in users.
````python
channel_list = dict()
logged_user_list = dict()
````
The method below performs the creation of the user and recording it in the cookies( [Requirement 1](#requirement-1) ).
````python
@app.route("/login", methods=['GET', 'POST'])
def  login():
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
````
The method below performs the user's logout excluding him from the cookies and from the dictionary logged_user_list.
````python
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
````
The method below performs the creation of a new channel and does not allow the creation of channels with repeated names([Requirement 2](#requirement-2)).
````python
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
 ````
 Method that receives the ID of a channel and displays all messages on that channel.
 
 ````python
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
````
The socket below is used to send messages to a group and send it back to the frontend.
````python
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
````
    The socket below receives a base64 string and other information, writes everything to the dictionary channel_list and then returns everything to the frontend([Requirement 7](#requirement-7)).
  ````python
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
 ````
 The rule below is valid if the "deck ()" has more than 100 records it removes an item from the end of the list and adds a new item at the beginning of the list.
 ````python
    if len(messages) > 100:
        messages.popleft()
    messages.append(message)
````
This snippet sends the message back to the frontend.
````python
    channel_list[current_channel] = messages
    emit('return message file', {
        'id': message.id,
        'timestamp': message.timestamp,
        'username': username,
        'filename': message.filename,
        'type': message.type.name,
        'is_delete': True,
        'msg': message.text}, room=current_channel)
   ````
   
   The socket below receives a message id and removes it from the deck () and then returns to the frontend that will delete the message there([Requirement 7](#requirement-7)).
 ````python
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
  ````
  the methods below are for entering and leaving a channel.
  ````python
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
````
