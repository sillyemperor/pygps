# -*- coding:utf8 -*-
import SocketServer
import binascii


class ProtocolTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        print binascii.b2a_hex(data), data
        self.request.sendall(data)


class ProtocolUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print binascii.b2a_hex(data), data
        socket.sendto(data, self.client_address)


# server = SocketServer.ThreadingTCPServer(('', 3007), ProtocolTCPRequestHandler)
server = SocketServer.ThreadingUDPServer(('', 3007), ProtocolUDPHandler)
server.serve_forever()


