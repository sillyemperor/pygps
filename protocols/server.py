# -*- coding:utf8 -*-
import SocketServer
import socket
import threading


class ProtocolTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        print data
        self.request.sendall(data)

server = SocketServer.ThreadingTCPServer(('localhost', 3007), ProtocolTCPRequestHandler)
server.serve_forever()
