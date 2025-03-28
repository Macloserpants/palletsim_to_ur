# server.py
# This program starts a server, receives request message then displays data.
import socket
import sys

# Used to safely terminate on keyboard interrupt.
def handle_keyboard_interrupt(client_socket, server_socket):
    print("Received KeyboardInterrupt, shutting down the server...")
    client_socket.close()
    server_socket.close()
    sys.exit(0)

# Used to receive the data in chunks and print it out.
def receive_data(client_socket, server_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print("Received data: {}".format(data.decode()))
    except KeyboardInterrupt:
        handle_keyboard_interrupt(client_socket, server_socket)

# Opens TCP socket, listens, binds then receives and displays data.
# Terminates safely when the client closes connection or keyboard interrupt.
def main():
    # HOST_IP_ADDRESS = socket.gethostbyname(socket.gethostname())
    HOST_IP_ADDRESS = "192.168.56.20"
    PORT = 50000 

    # create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((HOST_IP_ADDRESS, PORT))
    except socket.error as e:
        print("Error binding the socket: {}".format(e))
        sys.exit(1)

    try:
        server_socket.listen()
    except socket.error as e:
        print("Error listening on the socket: {}".format(e))
        sys.exit(1)

    print("Listening on {}:{}".format(HOST_IP_ADDRESS, PORT))

    print("Waiting for a connection...")
    try:
        client_socket, client_address = server_socket.accept()
    except socket.error as e:
        print("Error accepting a connection: {}".format(e))
        sys.exit(1)

    print("Accepted connection from {}".format(client_address))

    receive_data(client_socket, server_socket)

    # close the connection
    client_socket.close()
    server_socket.close()

if __name__ == '__main__':
    main()