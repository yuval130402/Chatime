__author__ = 'Yuval Cohen'
import socket
import select
import time
import Tkinter as tk
from Tkinter import *
import winsound
from winsound import *
PORT = 5678
IP = '127.0.0.1'


def send(event=None):
    global message
    global input_get
    global count
    input_get = str(input_field.get())
    if input_get != "" and input_get != "1" and input_get != "2" and input_get != "3" and input_get != "4":
        if (input_get[0] != "4") or (input_get[0] == "4" and len(input_get[1:]) <= 25 and input_get[1:] != lb["text"]):
            if input_get == "quit":
                my_socket.send(message + input_get)

            elif input_get == "view-managers" or input_get == "view-users" or input_get == "mute-on" or input_get == "mute-off":
                my_socket.send(message + input_get)

            else:
                message = message + input_get[0]
                input_get = input_get[1:]
                if len(input_get) < 10:
                    message = message + "00" + str(len(input_get)) + input_get
                else:
                    if len(input_get) < 100:
                        message = message + "0" + str(len(input_get)) + input_get
                    else:
                        message = message + str(len(input_get)) + input_get
                my_socket.send(message)

                if len(user) < 10:
                    message = "0" + str(len(user)) + "" + user
                else:
                    message = str(len(user)) + "" + user
        else:
            if input_get[1:] == lb["text"]:
                msg_list.insert(END, "This is the same chat name")
            else:
                msg_list.insert(END, "Invalid chat name-It must be 1-25 characters.")
            count = count + 1

        input_user.set('')  # Clears input field.
        input_field.delete(0, 'end')


def getting_massage():
    global closeOff_not
    global count
    global chat_name
    if closeOff_not:
        rlist, wlist, xlist = select.select([my_socket], [my_socket], [])
        if len(rlist) > 0:
            for current in rlist:
                data = current.recv(1024)
                if data == "":
                    my_socket.close()
                elif data == "You had been kicked from the chat" or data == "You have left the chat!":
                    msg_list.insert(END, data)
                    count = count + 1
                    closeOff_not = False
                    break
                else:
                    is_color = False
                    if data[0:12] == "colorMessage":
                        data = data[12:]
                        color_length = int(data[0])
                        data = data[1:]
                        color = data[0:color_length]
                        data = data[color_length:]
                        is_color = True
                    if data[0:10] == "changeChat":
                        data = data[10:]
                        chat_length = int(data[0:2])
                        data = data[2:]
                        chat_name = data[0:chat_length]
                        data = data[chat_length:]
                        lb["text"] = chat_name
                    if data[0:11] == "get_message":
                        winsound.PlaySound('getmessage.wav', winsound.SND_FILENAME | SND_ASYNC)
                        data = data[11:]
                    elif data[0:12] == "send_message":
                        winsound.PlaySound('send.wav', winsound.SND_FILENAME | SND_ASYNC)
                        data = data[12:]
                    while len(data) > 68:
                        part = data[0:68]
                        while part[-1] != " ":
                            part = part[0:-1]
                        data = data[len(part):]
                        msg_list.insert(END, part)
                        if is_color:
                            msg_list.itemconfig(count, foreground=color)
                        count = count + 1
                    if len(data) != 0:
                        msg_list.insert(END, data)
                        if is_color:
                            msg_list.itemconfig(count, foreground=color)
                        count = count + 1

    try:
        root.protocol("WM_DELETE_WINDOW", on_closing)
    except Exception:
        pass
    root.update()


def on_closing():
    global message
    global input_get
    input_get = "quit"
    my_socket.send(message + input_get)


def main():
    global my_socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))
    global user
    user = str(raw_input("write a name"))
    global chat_name
    while True:
        while len(user) > 16 or len(user) == 0 or user[0] == "@":
            user = str(raw_input("Invalid Username-It must be 1-16 characters and don't start with @. Try again."))
        my_socket.send("addUser" + user)
        valid = my_socket.recv(1024)
        if valid[0:17] == "Username is valid":
            if valid == "Username is valid-chat name":
                chat_name = str(raw_input("write a name for your chat"))
                while len(chat_name) > 25 or len(chat_name) == 0:
                    chat_name = str(raw_input("Invalid chat name-It must be 1-25 characters. Try again."))
                my_socket.send(chat_name)
            else:
                chat_name = valid[17:]
            break
        user = str(raw_input("Invalid Username- the user is exist. Try again."))

    global message
    if len(user) < 10:
        message = "0"+str(len(user)) + "" + user
    else:
        message = str(len(user)) + "" + user

    global root
    root = tk.Tk()
    tk_rgb = "#%02x%02x%02x" % (128, 192, 200)
    root["background"] = tk_rgb
    global lb
    lb = tk.Label(root, text=chat_name, bg="dark green", fg="white", font="Ariel 20 bold italic")
    lb.pack()
    root.title("Welcome "+user+" to our chat")

    global frame_messages
    frame_messages = tk.Frame(root, width="600", height="600", bg="LightBlue2")
    scrollbar = tk.Scrollbar(frame_messages)
    global msg_list
    msg_list = tk.Listbox(frame_messages, width="100", height="100", bd=3, font="Ariel 12 bold",
                          selectbackground="LightBlue3", selectforeground="gray50", yscrollcommand=scrollbar.set, bg="LightBlue2")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
    frame_messages.pack(side="top")
    frame_messages.pack_propagate(False)  # prevent frame to resize to the labels size
    label_send = tk.Label(root, width="100", height="40", font="Ariel 20 bold italic", bg="gray90")
    label_send.pack()
    global input_user
    input_user = tk.StringVar()
    global input_field
    input_field = tk.Entry(label_send, font='Arial 12', width="40", fg='black', text=input_user)
    input_field.bind("<Return>", send)
    input_field.pack(side="left", fill=X)
    global btn1
    btn1 = tk.Button(label_send, text='Send', command=send, relief="groove", padx=3, pady=3, bg="snow3")
    btn1.pack(side="right")

    global closeOff_not
    closeOff_not = True
    global count
    count = 0
    my_socket.send("showAddUser" + user)
    while True:
        if closeOff_not is False:
            my_socket.close()
            btn1['state'] = tk.DISABLED
            input_field['state'] = tk.DISABLED
            time.sleep(3)
            break
        else:
            getting_massage()


if __name__ == '__main__':
    main()
