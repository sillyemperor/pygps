import socket
import time
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
    print s.recv(1024)
    s.close()

if __name__ == '__main__':
    import binascii
    import gevent

    gevent.joinall([ gevent.spawn(udp_write, 'localhost', 3009, binascii.a2b_hex('29298000281086985400000014522400000000000000000000000078fbbec37ffc1900001e000000000000ea0d')) for i in range(100) ])

