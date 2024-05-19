import socket
import threading

import socket
import threading
import sys
HOST = '127.0.0.1'  
PORT = 7120

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Username, password, id. ID is used used in the subscription list
accounts = []
accounts.append(("salma001", "pass", 0))
accounts.append(("ahmed002", "hello", 1))
accounts.append(("ayman003", "yes", 2))

subscription_list = [[] for _ in range(len(accounts))]

subscription_list[0].append("ahmed002")
subscription_list[0].append("water")
subscription_list[2].append("ahmed002")

offline_messages_list = [
    ("salma001", "ayman003", "Hello test"),
    ("salma001", "ahmed002", "Hello there1"),
    ("salma001", "ahmed002", "Hello there2"),
    ("salma001", "ahmed002", "Hello there3"),
    ("salma001", "ahmed002", "Hello there4"),
    ("salma001", "ahmed002", "Hello there5"),
    ("salma001", "ahmed002", "Hello there6"),
    ("salma001", "ahmed002", "Hello there7"),
]

conn_list = []
all_message_list = []
hash_list = [("salma001", "python", "This language is easy #python"), ("ayman003", "python", "Hello there #python")]

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except OSError as msg:
    print('Bind failed. Error Code : ' + str(msg.errno) + ' Message ' + msg.strerror)
    sys.exit()


print('Socket bind complete')

# Start listening on socket
s.listen(10)
print('Socket now listening')


def get_uid(uname):
    for user in accounts:
        if user[0] == uname:
            return user[2]
    return -1


def edit_subs(conn, uname):
    global subscription_list
    uid = get_uid(uname)
    while True:
        msg = conn.recv(1024)
        if msg == b"q":
            return
        option, friend = msg.decode("utf-8").split("|")
        if option == "1":
            if get_uid(friend) >= 0:
                if friend in subscription_list[uid]:
                    if conn:
                        conn.send("edit_subs|Invalid|Already subscribed!".encode("utf-8"))
                    continue
                else:
                    subscription_list[uid].append(friend)
                    if conn:
                        conn.send(
                            ("edit_subs|valid|You are now subscribed to " + friend).encode("utf-8")
                        )
                    return
            else:
                if conn:
                    conn.send(
                        ("edit_subs|Invalid|" + friend + " is not a valid username").encode(
                            "utf-8"
                        )
                    )
        elif option == "2":
            subs_list = ""
            for user in subscription_list[uid]:
                subs_list = subs_list + user + "\n"
            conn.send(("edit_subs|" + subs_list).encode("utf-8"))
            drop = conn.recv(1024).decode("utf-8")
            if drop not in subscription_list[uid]:
                conn.send("edit_subs|Invalid".encode("utf-8"))
                continue
            else:
                subscription_list[uid].remove(drop)
                conn.send("edit_subs|valid".encode("utf-8"))
                return
        elif option == "3":
            print(friend)
            subscription_list[uid].append(friend)
            return




def post_message(conn, uname):
    global offline_messages_list
    global conn_list
    global all_message_list

    msg = conn.recv(1024)
    if msg == b'q':
        return
    received_flag = False
    message = msg.decode("utf-8")

    all_message_list.append(uname + "|" + message)

    for user in accounts:
        received_flag = False
        if user[0] == uname:
            continue
        elif uname in subscription_list[user[2]]:
            for connection in conn_list:
                if user[0] == connection[0]:
                    received_flag = True
                    connection[1].send(("post|" + uname + "|" + message).encode("utf-8"))
            if not received_flag:
                offline_messages_list.append((user[0], uname, message))

# ...


def send_offline_msg(conn, uname):
    global offline_messages_list
    remove_list = []
    count = 0
    for msg in reversed(offline_messages_list):
        if msg[0] == uname:
            count += 1
            conn.send(("offline_msg|" + msg[1] + "|" + msg[2]).encode("utf-8"))
            conn.recv(1024)
            remove_list.append(msg)
            if count == 10:
                break

    for msg in remove_list:
        offline_messages_list.remove(msg)


def logout(conn, uname):
    global conn_list
    conn_list.remove((uname, conn))
    print(uname + " has signed out")
    threading.exit()


def see_followers(conn, uname):
    index = 0
    for sub in subscription_list:
        if uname in sub:
            for account in accounts:
                if index == account[2]:
                    conn.send(("see_followers|" + account[0]).encode("utf-8"))
                    conn.recv(1024)
        index += 1
    conn.send("see_followers|done".encode("utf-8"))
    return


def run(conn, uname):
    send_offline_msg(conn, uname)
    while True:
        option = conn.recv(1024).decode("utf-8")
        if option == "2":
            edit_subs(conn, uname)
        elif option == "3":
            post_message(conn, uname)
        elif option == "4":
            logout(conn, uname)
        elif option == "5":
            see_followers(conn, uname)
        else:
            conn.send("Invalid".encode("utf-8"))


def signin(conn):
    global conn_list
    while True:
        user_info = conn.recv(1024).decode("utf-8")
        uname, password = user_info.split("|")
        for user in accounts:
            if user[0] == uname and user[1] == password:
                conn.send("signin|valid".encode("utf-8"))
                conn.recv(1024)
                conn_list.append((uname, conn))
                print(uname + " has signed in")
                return run(conn, uname)
        conn.send("signin|Invalid".encode("utf-8"))


def admin():
    global subscription_list
    global accounts
    while True:
        option = input("")
        if option == "messagecount":
            print(len(all_message_list))
        elif option == "usercount":
            print(len(conn_list))
        elif option == "storedcount":
            print(len(offline_messages_list))
        elif option == "newuser":
            uname = input("Username: ")
            password = input("Password: ")
            accounts.append((uname, password, accounts[len(accounts) - 1][2] + 1))
            subscription_list.append([])


threading.Thread(target=admin).start()

while True:
    conn, addr = s.accept()
    print("Connected with {}:{}".format(addr[0], addr[1]))
    threading.Thread(target=signin, args=(conn,)).start()

s.close()
