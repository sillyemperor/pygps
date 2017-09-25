# -*- coding:utf8 -*-

import binascii
from cStringIO import StringIO
import logging


class ProtocolTCPHandler:
    def __init__(self, translator, pusher, user_signal=None):
        self.translator = translator
        self.pusher = pusher
        self.user_signal=user_signal

    def __call__(self, request, client_address, server):
        buff = StringIO()
        while 1:
            b = request.recv(1024)
            if not b:
                break
            buff.write(b)
        data = buff.getvalue()
        try:
            result, response, input_data = self.translator.on_message(data)
            if response:
                request.sendall(binascii.a2b_hex(response))
            self.pusher.push(result)
            if self.user_signal:
                for sid, name in self.user_signal.getall(result.imei):
                    signal = self.translator.build_signal(name, input_data)
                    if signal:
                        request.sendall(binascii.a2b_hex(signal))
                    self.user_signal.mark_read(sid)
        except Exception as e:
            logging.error('route fail err=%s input_data=%s ', e, input_data)


class ProtocolUDPHandler:
    def __init__(self, translator, pusher, user_signal=None):
        self.translator = translator
        self.pusher = pusher
        self.user_signal=user_signal

    def __call__(self, request, client_address, server):
        data = request[0].strip()
        socket = request[1]
        try:
            result, response, input_data = self.router.on_message(data)
            if response:
                socket.sendto(binascii.a2b_hex(response), client_address)
            self.pusher.push(result)
            if self.user_signal:
                for sid, name in self.user_signal.getall(result.imei):
                    signal = self.translator.build_signal(name, input_data)
                    if signal:
                        request.sendall(binascii.a2b_hex(signal))
                    self.user_signal.mark_read(sid)
        except Exception as e:
            logging.error('route fail err=%s input_data=%s ', e, input_data)

