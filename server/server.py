# -*- coding:utf8 -*-
import SocketServer
from handlers import ProtocolUDPHandler, ProtocolTCPHandler
import logging


def init_log(level, name, path='', dir='/tmp/logs'):
    import logging.handlers
    import os.path

    file_folder = os.path.join(dir, path)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)
    file_path = os.path.join(file_folder, name)
    handler = logging.handlers.RotatingFileHandler(
        file_path, maxBytes=1048576, backupCount=5)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(asctime)s %(thread)d %(levelno)s  %(pathname)s %(lineno)d %(funcName)s %(message)s'))
    logging.getLogger().addHandler(handler)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(asctime)s %(thread)d %(levelno)s  %(pathname)s %(lineno)d %(funcName)s %(message)s'))
    logging.getLogger().addHandler(handler)


def run_udp_server(translator, port, pusher, user_signal=None):
    init_log(logging.DEBUG, name='%s.log'%translator.__class__.__name__, path=translator.__module__)
    server = SocketServer.ThreadingUDPServer(('', port), ProtocolUDPHandler(translator, pusher, user_signal))
    server.serve_forever()


def run_tcp_server(translator, port, pusher, user_signal=None):
    init_log(logging.DEBUG, name='%s.log'%translator.__class__.__name__, path=translator.__module__)
    server = SocketServer.ThreadingTCPServer(('', port), ProtocolTCPHandler(translator, pusher, user_signal))
    server.serve_forever()




