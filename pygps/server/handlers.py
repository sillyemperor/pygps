# -*- coding:utf8 -*-
import logging
from twisted.internet import protocol
from twisted.protocols.policies import TimeoutMixin
import traceback


class ProtocalTCPHandler(protocol.Protocol, TimeoutMixin):
    connection_list = []
    def __init__(self, translator, pusher, user_signal=None):
        self.translator = translator
        self.pusher = pusher
        self.user_signal=user_signal

    def connectionMade(self):
        ip = self.transport.client[0]
        reconnected = ip in ProtocalTCPHandler.connection_list
        ProtocalTCPHandler.connection_list.append(ip)
        logging.error('%s connected', ip)
        if reconnected:
            logging.error('%s reconnected %s times', ip, ProtocalTCPHandler.connection_list.count(ip))

    def connectionLost(self, reason):
        ProtocalTCPHandler.connection_list.remove(self.transport.client[0])
        logging.error('%s lost connection by %s', self.transport.client[0], reason)
        self.setTimeout(None)

    def dataReceived(self, data):
        # logging.error('receive data')
        try:
            result, response, input_data = self.translator.on_message(data)
            if response:
                self.transport.write(self.translator.encode_data(response))
            self.pusher.push(result)
            if self.user_signal:
                try:
                    for sid, name in self.user_signal.get_all_signal(result.imei):
                        signal = self.translator.build_signal(name, input_data)
                        if signal:
                            self.transport.write(self.translator.encode_data(signal))
                        self.user_signal.mark_read_signal(sid)
                except Exception as e:
                    logging.error('err=%s', e)
        except Exception as e:
            logging.error('err=%s', e)
            traceback.print_exc()


class ProtocalTCPFactory(protocol.Factory):
    def __init__(self, translator, pusher, user_signal, clazz=ProtocalTCPHandler):
        self.clazz = clazz
        self.translator = translator
        self.pusher = pusher
        self.user_signal=user_signal
    def buildProtocol(self, addr):
        return self.clazz(self.translator, self.pusher, self.user_signal)


class ProtocalUDPHandler(protocol.DatagramProtocol):
    def __init__(self, translator, pusher, user_signal=None):
        self.translator = translator
        self.pusher = pusher
        self.user_signal=user_signal

    def datagramReceived(self, data, (host, port)):
        logging.debug('receive %s', data)
        try:
            result, response, input_data = self.translator.on_message(data)
            if response:
                self.transport.write(self.translator.encode_data(response), (host, port))
            self.pusher.push(result)
            if self.user_signal:
                for sid, name in self.user_signal.get_all_signal(result.imei):
                    signal = self.translator.build_signal(name, input_data)
                    if signal:
                        self.transport.write(self.translator.encode_data(signal), (host, port))
                    self.user_signal.mark_read_signal(sid)
        except Exception as e:
            logging.error('err=%s', e)
            traceback.print_exc()
