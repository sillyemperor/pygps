import socket
from cStringIO import StringIO

def read_all(sock):
    buff = StringIO()
    while 1:
        b = sock.recv(1024)
        if not b:
            break
        buff.write(b)
    return buff.getvalue()


def tcp_write(host, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(content)
    s.close()


def udp_write(host, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(content, (host, port))
    s.close()
