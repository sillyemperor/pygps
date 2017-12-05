# -*- coding:utf8 -*-
import logging
from twisted.internet import reactor
from pygps.server.handlers import ProtocalTCPFactory, ProtocalUDPHandler
from pygps.server.pusher import ThreadQueuePusher
from pygps.goodhope.dal import GPSDal
from pygps.protocol.bsj import A5, Km
from pygps.protocol.longhan import Longhan16m
from pygps.protocol.xinan import Xinan
from pygps.protocol.qnm import Qnm
from pygps.protocol.xinji import Xinji


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
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelno)s %(thread)d %(pathname)s %(lineno)d %(funcName)s %(message)s'))
    logging.getLogger().addHandler(handler)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelno)s %(thread)d %(pathname)s %(lineno)d %(funcName)s %(message)s'))
    logging.getLogger().addHandler(handler)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='启动GPS前置机服务')
    parser.add_argument('translator', help="协议名称：A5,Km,Longhan16m,Xinan,Qnm,Xinji")
    parser.add_argument('connection', help="数据库连接字符串")
    parser.add_argument('-p', help="监听端口号", default='3007')
    parser.add_argument('-P', help="使用TCP or UDP 缺省为TCP", default='TCP')

    args = parser.parse_args()

    init_log(logging.DEBUG, '{translator}_{protocol}_{port}.log'.format(
        translator=args.translator, protocol=args.P, port=args.p
    ), dir='./logs')

    logging.info('start with %s', args)

    #
    dal1 = GPSDal(args.connection)
    dal2 = GPSDal(args.connection)
    pusher = ThreadQueuePusher(dal=dal1)
    translator = globals()[args.translator]()
    port = int(args.p)

    if args.P == 'TCP':
        reactor.listenTCP(port, ProtocalTCPFactory(translator=translator, pusher=pusher, user_signal=dal2))
    else:
        reactor.listenUDP(port,ProtocalUDPHandler(translator=translator, pusher=pusher, user_signal=dal2))

    reactor.run()
