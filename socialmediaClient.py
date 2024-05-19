import socket

HOST = '127.0.0.1'  # Server IP address
PORT = 7120           # Server port

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        client_socket.settimeout(5)  # a timeout of 5 seconds
        print("Connected to the server.")

        while True:
            print("\n1. Sign In\n2. Quit")
            choice = input("Enter your choice: ")

            if choice == "1":
                username = input("Enter your username: ")
                password = input("Enter your password: ")
                user_info = f"{username}|{password}"
                print(f"Sending: {user_info}")
                client_socket.send(user_info.encode("utf-8"))

                try:
                    response = client_socket.recv(1024).decode("utf-8")
                    print(f"Received: {response}")
                except socket.timeout:
                    print("Server response timed out. Please try again.")
                    continue

                if response == "signin|valid":
                    print("Sign in successful!\n")
                    interact_with_server(client_socket, username)
                else:
                    print("Invalid username or password. Please try again.")

            elif choice == "2":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")


def interact_with_server(client_socket, username):
    while True:
        print("\n1. Edit Subscriptions\n2. Post a Message\n3. Logout")
        print("4. See Followers\n5. Quit")
        option = input("Enter your option: ")

        client_socket.send(option.encode("utf-8"))

        if option == "1":
            edit_subscriptions(client_socket, username)
        elif option == "2":
            post_message(client_socket, username)
        elif option == "3":
            print("Logging out...")
            break
        elif option == "4":
            see_followers(client_socket)
        elif option == "5":
            print("Quitting...")
            break
        else:
            print("Invalid option. Please try again.")

def edit_subscriptions(client_socket, username):
    while True:
        print("\n1. Subscribe to a User\n2. Unsubscribe from a User\n3. Go Back")
        choice = input("Enter your choice: ")

        if choice == "1":
            friend = input("Enter the username to subscribe: ")
            message = f"1|{friend}"
            client_socket.send(message.encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            print(response)
        elif choice == "2":
            message = "2"
            client_socket.send(message.encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            print(response)
            if response == "edit_subs|done":
                break
            friend = input("Enter the username to unsubscribe: ")
            message = f"2|{friend}"
            client_socket.send(message.encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            print(response)
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")



def post_message(client_socket, username):
    message = input("Enter your message: ")
    payload = f"{message}"
    client_socket.send(payload.encode("utf-8"))
    response = client_socket.recv(1024).decode("utf-8")
    print(response)

# ...



def search(client_socket):
    word = input("Enter the hash tag to search: ")
    client_socket.send(word.encode("utf-8"))
    response = client_socket.recv(1024).decode("utf-8")
    print("Server response:", response)
    if response == "search|invalid":
        print("No matching hash tag found.")
    else:
        print(response)

def see_followers(client_socket):
    response = client_socket.recv(1024).decode("utf-8")
    if response.startswith("see_followers|done"):
        print("No followers found.")
    else:
        followers = response.split("|")[1:]
        print("Followers:")
        for follower in followers:
            print(follower)

if __name__ == "__main__":
    main()
