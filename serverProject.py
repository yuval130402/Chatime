__author__ = 'Yuval Cohen'
import socket
import select
from datetime import datetime
IP = '0.0.0.0'
PORT = 5678


def validation(name):
    # Checks if a specific name is in the Users list, returns true/false.
    for i in users:
        if i.get("username") == name:
            return True
    return False


def indexUser(current_socket):
    # gets a specific socket, returns the number of this socket in the Users list.
    count = 0
    for i in users:
        if i.get("socket") == current_socket:
            return count
        count = count+1


def User(name):
    # gets a specific name, return the user object in the Users list of this name.
    for i in users:
        if i.get("username") == name:
            return i


def User2(current_socket):
    # gets a specific socket, return the user object in the Users list of this socket.
    for i in users:
        if i.get("socket") == current_socket:
            return i


def color_appear(color):
    # gets a specific color and checks if the color is used by a user in User list, returns true/false.
    for i in users:
        if i.get("color") == color:
            return True
    return False


def send_add_user(current_socket, wlist, data):
    # sends that a specific user join the chat.
    time = str(datetime.now().strftime('%H:%M'))
    for client in users:
        if client.get("socket") is not current_socket:
            client.get("socket").send(time + " " + data + " joined to the chat")
        else:
            client.get("socket").send(time + " you joined to the chat")


def send_waiting_messages(wlist):
    # Sends waiting messages that need to be sent, only if the client's socket is writable.#
    global mute_on
    for mes in messages_to_send:
        (client_socket, data) = mes
        messages_to_send.remove(mes)
        time = str(datetime.now().strftime('%H:%M'))
        if message[2] == 2:
            if message[1] in managers and validation(message[4]):
                managers.append(message[4])
                current = User(message[4])
                for client in wlist:
                    if client is not client_socket:
                        if client is current.get("socket"):
                            client.send(time + " You appointed by @" + message[1] + " as a manager")
                        else:
                            client.send(time + " " + message[4] + " appointed by @" + message[1] + " as a manager")
                    if client is client_socket:
                        client.send(time + " You appointed " + message[4] + " as a manager")
            else:
                if message[1] not in managers:
                    client_socket.send("You are not a manager")
                else:
                    client_socket.send(message[4] + " is not exist in this chat")

        elif message[2] == 3:
            if message[1] in managers and validation(message[4]):
                current = User(message[4])
                users.remove(current)
                open_client_sockets.remove(current.get("socket"))
                this_color = current.get("color")
                colors.remove(this_color)
                add = 0
                for cl in colors:
                    if color_appear(cl) is True:
                        colors.insert(add, this_color)
                        break
                    add = add+1
                if message[4] in managers:
                    managers.remove(message[4])
                for client in wlist:
                    if client is not client_socket:
                        if client is current.get("socket"):
                            client.send("You had been kicked from the chat")
                        else:
                            client.send(time + " " + message[4] + " has been kicked from the chat by @" + message[1])
                    if client is client_socket:
                        client.send(time + " You kicked " + message[4] + " from the chat")
            else:
                if message[1] not in managers:
                    client_socket.send("You are not a manager")
                else:
                    client_socket.send(message[4] + " is not exist in this chat")

        elif message[2] == 4:
            if (mute_on is True) and (message[1] not in managers):
                client_socket.send("Silent mode - you can't change the chat name")
            else:
                if message[3] < 10:
                    chat_length = "0" + str(message[3])
                else:
                    chat_length = str(message[3])
                if message[1] in managers:
                    message[1] = "@" + message[1]
                for client in wlist:
                    if client is not client_socket:
                        client.send("changeChat" + chat_length + message[4] + time + " " + message[1] + " changed the name of the chat to: " + message[4])
                    if client is client_socket:
                        client.send("changeChat" + chat_length + message[4] + time + " You changed the name of the chat to: " + message[4])

        elif message[2] == "mute-on":
            if message[1] in managers:
                if mute_on is False:
                    mute_on = True
                    for client in wlist:
                        if client is not client_socket:
                            client.send(time + " Silent mode has been enabled by @" + message[1] + ": Only managers can write messages")
                        if client is client_socket:
                            client.send(time + " You have enabled silent mode: Only managers can write messages")
                else:
                    client_socket.send("Silent mode has already been enabled")
            else:
                client_socket.send("You are not a manager")

        elif message[2] == "mute-off":
            if message[1] in managers:
                if mute_on is True:
                    mute_on = False
                    for client in wlist:
                        if client is not client_socket:
                            client.send(time + " Silent mode has been stopped by @" + message[1] + ": Everyone can write messages")
                        if client is client_socket:
                            client.send(time + " You have stopped silent mode: Everyone can write messages")
                else:
                    client_socket.send("Silent mode was not enabled before")
            else:
                client_socket.send("You are not a manager")

        elif message[2] == "view-managers":
            mgr = ""
            for x in managers:
                mgr = mgr + x + ", "
            mgr = mgr[0:-2]
            if len(managers) == 1:
                client_socket.send("There is one manager: " + mgr)
            else:
                client_socket.send("There are " + str(len(managers)) + " managers: " + mgr)

        elif message[2] == "view-users":
            usr = ""
            for x in users:
                usr = usr + x.get("username") + ", "
            usr = usr[0:-2]
            if len(users) == 1:
                client_socket.send("There is one user: " + usr)
            else:
                client_socket.send("There are " + str(len(users)) + " users: " + usr)

        else:
            if message[2] != "quit" and (mute_on is True) and (message[1] not in managers):
                client_socket.send("Silent mode - you can't speak here")
            else:
                if message[1] in managers:
                    if message[2] == "quit":
                        managers.remove(message[1])
                        if len(managers) == 0 and len(users) != 0:
                            managers.append(users[0].get("username"))
                    message[1] = "@" + message[1]
                current = User2(client_socket)
                for client in wlist:
                    if client is not client_socket:
                        if message[2] == "quit":
                            client.send(time + " " + message[1] + " has left the chat!")
                        else:
                            client.send("colorMessage" + str(len(current.get("color"))) + current.get("color")
                                        + "get_message" + time + " " + message[1] + ": " + message[4])
                    if client is client_socket:
                        if message[2] == "quit":
                            client.send("You have left the chat!")
                        else:
                            client.send("colorMessage" + str(len(current.get("color"))) + current.get("color")
                                        + "send_message" + time + " You: " + message[4])


def main():
    server_socket = socket.socket()
    server_socket.bind((IP, PORT))
    server_socket.listen(10)
    global open_client_sockets
    open_client_sockets = []
    global messages_to_send
    messages_to_send = []
    global managers
    managers = []
    global users
    users = []
    global rlist
    global mute_on
    mute_on = False
    global colors
    colors = ["orange", "purple", "blue", "green3", "hot pink", "red", "gray20", "yellow", "brown", "chocolate", "navy"]
    chat_name = ""
    while True:
        rlist, wlist, xlist = select.select([server_socket] + open_client_sockets,  open_client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                (new_socket, address) = server_socket.accept()
                open_client_sockets.append(new_socket)
            else:
                data = current_socket.recv(1024)
                if data[0:7] == "addUser":
                    if validation(data[7:]) is True:
                        current_socket.send("Username is invalid")
                    else:
                        name = True
                        if len(users) == 0:
                            name = False
                        users.append({"socket": current_socket, "username": data[7:], "color": colors[0]})
                        this_color = colors.pop(0)
                        colors.append(this_color)
                        if len(managers) == 0:
                            managers.append(data[7:])
                        if name is False:
                            current_socket.send("Username is valid-chat name")
                            chat_name = current_socket.recv(1024)
                        else:
                            current_socket.send("Username is valid" + chat_name)
                elif data[0:11] == "showAddUser":
                    send_add_user(current_socket, wlist, data[11:])
                else:
                    global message
                    message = []
                    a = False
                    if data[len(data)-4:len(data)] == "quit":
                        message.append(int(data[0:2]))
                        data = data[2:]
                        message.append(data[0:message[0]])
                        data = data[message[0]:]
                        message.append(data)

                        current = User(message[1])
                        users.pop(indexUser(current_socket))
                        open_client_sockets.remove(current_socket)
                        this_color = current.get("color")
                        colors.remove(this_color)
                        add = 0
                        for cl in colors:
                            if color_appear(cl) is True:
                                colors.insert(add, this_color)
                                break
                            add = add + 1
                    else:
                        message.append(int(data[0:2]))
                        data = data[2:]
                        message.append(data[0:message[0]])
                        data = data[message[0]:]
                        if data == "view-managers" or data == "view-users" or data == "mute-on" or data == "mute-off":
                            message.append(data)
                        else:
                            try:
                                message.append(int(data[0]))
                                message.append(int(data[1:4]))
                                message.append(data[4:])
                            except Exception:
                                current_socket.send("Message without a usage command")
                                a = True

                    if a is False:
                        messages_to_send.append((current_socket, message))
                        send_waiting_messages(wlist)


if __name__ == '__main__':
    main()
