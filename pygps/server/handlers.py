# -*- coding:utf8 -*-
import logging

from twisted.internet import protocol
from twisted.protocols.policies import TimeoutMixin


class ProtocalTCPHandler(protocol.Protocol,TimeoutMixin):
    def __init__(self, translator, pusher, user_signal=None):
        self.translator = translator
        self.pusher = pusher
        self.user_signal=user_signal

    def connectionMade(self):
            pass

    def makeConnection(self, transport):
        self.transport = transport
        logging.info('%s connected', transport)

    def connectionLost(self, reason):
        logging.info('%s lost connection by %s', self.transport, reason)
        self.setTimeout(None)

    def timeoutConnection(self):
        logging.info('%s timeout', self.transport)

    def dataReceived(self, data):
        try:
            result, response, input_data = self.translator.on_message(data)
            print result, response, input_data
            if response:
                self.transport.write(self.translator.encode_data(response))
            self.pusher.push(result)
            if self.user_signal:
                for sid, name in self.user_signal.get_all_signal(result.imei):
                    signal = self.translator.build_signal(name, input_data)
                    if signal:
                        self.transport.write(self.translator.encode_data(signal))
                    self.user_signal.mark_read_signal(sid)
        except Exception as e:
            logging.error('route fail err=%s input_data=%s ', e, input_data)


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
        input_data = data
        try:
            result, response, input_data = self.translator.on_message(data)
            print result, response, input_data
            if response:
                self.transport.write(self.translator.encode_data(response),(host, port))
            self.pusher.push(result)
            if self.user_signal:
                for sid, name in self.user_signal.get_all_signal(result.imei):
                    signal = self.translator.build_signal(name, input_data)
                    if signal:
                        self.transport.write(self.translator.encode_data(signal),(host, port))
                    self.user_signal.mark_read_signal(sid)
        except Exception as e:
            logging.error('route fail err=%s input_data=%s ', e, input_data)
