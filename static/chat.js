
// Connect to websocket
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
document.addEventListener('DOMContentLoaded', () => {
    socket.on('connect', () => {
        document.querySelector('#txMessage').addEventListener("keyup", function (event) {
            if (event.keyCode === 13) {
                event.preventDefault();
                const message = document.querySelector('#txMessage').value;
                if (message != "") {
                    socket.emit('send message', message);
                    document.querySelector('#txMessage').value = "";
                }
                return false;
            }
        });

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

        document.querySelectorAll("[id^='btn_delete_message_']").forEach(function (button) {
            button.onclick = function () {
                let id = this.dataset.id;
                socket.emit('delete message', id);
            }
        });

        document.querySelector('#file_upload').onchange = function () {
            var file = this.files[0],
                reader = new FileReader();
            reader.onloadend = function () {
                var b64 = reader.result;
                socket.emit('send file', b64, file.name, file.type);
            };

            reader.readAsDataURL(file);
        };
    });

    socket.on('return message', data => {
        sendMessenger(data);
    });

    socket.on('return message file', data => {
        sendMessenger(data);
    });

    socket.on('room status', data => {
        sendMessenger(data);
    });

    socket.on('return deleted message', data => {
        if (data.id != "undefined") {
            document.querySelector('#id_' + data.id).remove();
        }
    });

    let last_channel = localStorage.getItem('last_channel');

    if (last_channel != "" && current_channel == "") {
        localStorage.removeItem('last_channel');
    } else {
        socket.emit('join a room');
        $("#txMessage").prop("disabled", false);
        localStorage.setItem('last_channel', current_channel)
    }
});

function sendMessenger(data) {

    let div_class = "container darker";
    let span_class = "time-left";
    let h3_class = "right";

    if (current_username == data.username) {
        div_class = "container";
        span_class = "time-right";
        h3_class = "";
    }

    const br = document.createElement('BR');
    const div = document.createElement('div');
    const button = document.createElement('BUTTON');
    const span2 = document.createElement('span');
    const h3 = document.createElement('h3');
    const a = document.createElement('A');
    var img = document.createElement("IMG");
    const p = document.createElement('p');
    const span = document.createElement('SPAN');
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
            let id = this.dataset.id;
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
    } else if (data.type == "OTHER") {
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
        var chatList = document.getElementById('chat_list');
        chatList.scrollTop = chatList.scrollHeight;
    }, 100);

}