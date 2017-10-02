# -*- coding:utf8 -*-
"""消息处理的基础类"""
import binascii


class ProtocolTranslator:
    def main_signaling(self, s):
        """
        获取主信令
        :param s: 转换后的设备输入
        :return:
        """
        raise NotImplementedError()

    def build_response(self, s, ms):
        """
        构建与主信令相关的回复
        :param s: 转换后的设备输入
        :return:
        """
        pass

    def build_signal(self, name):
        """
        构建下发指令
        :param name: 指令名称，由平台定义
        :return:
        """
        pass

    def decode_data(self, data):
        """
        设备输入转换，例如：从字节流转成16进制字符串
        :param data: 设备输入
        :return:
        """
        return binascii.b2a_hex(data)

    def encode_data(self, s):
        """
        设备输出转换，例如：从16进制字符串转成字节流
        :param s:
        :return:
        """
        return s.decode("hex")

    def on_main_signaling(self, s, ms):
        raise NotImplementedError('Unknown main signaling %s data=%s' % (ms, s))

    def route_message(self, ms, s):
        func_name = 'on_ms_%s'%ms
        if not hasattr(self, func_name):
            return self.on_main_signaling(ms, s)
        else:
            func = getattr(self, func_name)
            if not callable(func):
                raise StandardError('%s is not callable data=%s' % (func_name, s))
            return func(s)

    def do_response(self, s, ms):
        func_name = 'on_ms_resp_%s'%ms
        if not hasattr(self, func_name):
            return self.build_response(ms, s)
        else:
            func = getattr(self, func_name)
            if not callable(func):
                raise StandardError('%s is not callable data=%s' % (func_name, s))
            return func(s)

    def on_message(self, data):
        """
        处理入口
        :param data: 设备输入
        :return: 解析后的结果，向设备的回复，转换后的设备输入
        """
        s = self.decode_data(data)
        ms = str(self.main_signaling(s)).lower()
        return self.route_message(s, ms), self.do_response(s, ms), s
