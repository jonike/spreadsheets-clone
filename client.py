import socket
import _thread

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 3162)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)


def clientthread():
    while 1:
        lengt = sock.recv(10)
        if not lengt.strip():
            continue
        length = int(lengt.decode())
        data = sock.recv(length).decode()
        print('Received from server: ' + data)
        print("\n -> ", end="")

t = _thread.start_new_thread(clientthread, ())


message = input(" -> ")

while message != 'q':
    if not message.strip():
        continue
    lengt = '{:10d}'.format(len(message))
    sock.send(lengt.encode())
    sock.send(message.encode())
    message = input(" -> ")
