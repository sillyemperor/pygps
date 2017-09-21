# -*- coding:utf8 -*-
"""消息处理的基础类"""
import binascii


class MessageRouter:
    def main_signaling(self, s):
        raise NotImplementedError()
    def build_response(self, s):
        pass

    def route_message(self, s):
        ms = 'on_ms_%s'%str(self.main_signaling(s)).lower()
        if not hasattr(self, ms):
            raise NotImplementedError('Unknown main signaling %s' % ms)
        func = getattr(self, ms)
        if not callable(func):
            raise StandardError('%s is not callable'%ms)
        return func(s)

    def prepare_data(self, data):
        return binascii.b2a_hex(data)

    def on_message(self, data):
        s = self.prepare_data(data)
        return self.route_message(s), self.build_response(s)
