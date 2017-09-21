# -*- coding:utf8 -*-

from gevent import socket
from gevent.server import StreamServer
from cStringIO import StringIO

def handle_echo(sock, address):
    buff = StringIO()
    while True:
        data = sock.recv(1024)
        if not data:
            break
        buff.write(data)
    print buff.getvalue()
    socket.close()

server = StreamServer(("", 2345), handle_echo)
server.server_forever()