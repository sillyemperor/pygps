# -*- coding:utf8 -*-
import logging
from twisted.internet import reactor
from server.handlers import ProtocalTCPFactory, ProtocalUDPHandler
from server.pusher import ThreadQueuePusher
from goodhope.dal import GPSDal
from protocol.bsj import A5, Km
from protocol.longhan import Longhan16m
from protocol.xinan import Xinan
from protocol.qnm import Qnm


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
    parser.add_argument('translator', help="协议名称：A5,Km,Longhan16m,Xinan,Qnm")
    parser.add_argument('connection', help="数据库连接字符串")
    parser.add_argument('-p', help="监听端口号", default='3007')
    parser.add_argument('-P', help="使用TCP or UDP 缺省为TCP", default='TCP')

    args = parser.parse_args()

    init_log(logging.INFO, '%s.log'%args.translator)

    logging.info('start with %s', args)

    #
    dal = GPSDal(args.connection)
    pusher = ThreadQueuePusher(dal=dal)
    translator = globals()[args.translator]()
    port = int(args.p)

    if args.P == 'TCP':
        reactor.listenTCP(port, ProtocalTCPFactory(translator=translator, pusher=pusher, user_signal=dal))
    else:
        reactor.listenUDP(port,ProtocalUDPHandler(translator=translator, pusher=pusher, user_signal=dal))

    reactor.run()
