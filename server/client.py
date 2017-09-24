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
    # tcp_write('localhost', 3007, binascii.a2b_hex('2929800032150b1a94170921213448028412051214493700000102fc15480aaffddff8001e00000000000000080010013121112620740d'))
    udp_write('localhost', 3007, binascii.a2b_hex('2929800032150b1a94170921213448028412051214493700000102fc15480aaffddff8001e00000000000000080010013121112620740d'))
