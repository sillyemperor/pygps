# -*- coding:utf8 -*-
import logging
import client


def send_data(host, port, protocol, data):
    if 'TCP' == protocol:
        client.tcp_write(host, port, data)
    else:
        client.udp_write(host, port, data)

if __name__ == '__main__':
    import binascii
    import argparse
    parser = argparse.ArgumentParser(description='启动数据木模拟程序')
    parser.add_argument('-H', help="目标主机，缺省'localhost'", default='localhost')
    parser.add_argument('-p', help="目标端口号，缺省'3007'", default='3007')
    parser.add_argument('-P', help="使用TCP or UDP 缺省为TCP", default='TCP')
    parser.add_argument('-d', help="数据，如果为空则必须提供'-f'参数")
    parser.add_argument('-f', help="数据文件，如果为空则必须提供'-d'参数")

    args = parser.parse_args()
    if not args.d and not args.f:
        parser.print_help()

    print args

    if args.d:
        send_data(args.H, int(args.p), args.P, binascii.a2b_hex(args.d))
    else:
        with open(args.f, 'r') as fp:
            for i in fp.readlines():
                try:
                    send_data(args.H, int(args.p), args.P, binascii.a2b_hex(i.strip()))
                except Exception as ex:
                    logging.error('send fail %s', ex)