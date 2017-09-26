# -*- coding:utf8 -*-
import logging
from twisted.internet import reactor
from server.handlers import ProtocalTCPFactory, ProtocalUDPHandler
from server.pusher import ThreadQueuePusher
from goodhope.dal import GPSDal


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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='启动GPS前置机服务')
    parser.add_argument('-c', help="数据库连接字符串")
    args = parser.parse_args()

    if not args.c:
        print parser.print_help()

    dal = GPSDal(args.c)

# reactor.listenTCP(5001,ProtocalTCPFactory(QNMTCP))
