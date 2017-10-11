# -*- coding:utf8 -*-
"""博实结"""
from protocol import ProtocolTranslator
from result import Location, Identity
import datetime
import logging
import struct


class A5(ProtocolTranslator):
    """A5"""
    @staticmethod
    def sum(s):
        a = "00"
        for i in range(0, len(s), 2):
            tmp = (int(a, 16)) ^ (int(s[i:i + 2], 16))
            a = hex(tmp)[2:].zfill(2)
        return a

    @staticmethod
    def imei(a):
        b = [int(a[:2], 16), int(a[2:4], 16), int(a[4:6], 16), int(a[6:], 16)]
        c = map(lambda x: x > int('80', 16) and (1, x - int('80', 16)) or (0, x), b)
        d = ['%d' % i[0] for i in c]
        e = ['%02d' % i[1] for i in c]
        return '%s%s' % (int(''.join(d), 2) + 130, ''.join(e))

    def main_signaling(self, s):
        return s[4:6]

    def build_response(self, s):
        res = "210005" + s[-4:-2] + s[4:6] + s[18:20]
        restr = "2929" + res + A5.sum(res) + "0d"
        return restr.upper()

    def on_ms_80(self, s):
        imei = A5.imei(s[10:18])
        # log
        timestr = s[18:30]
        logstr = s[30:38]
        latstr = s[38:46]
        speedstr = s[46:50]
        dirstr = s[50:54]
        Bstr = s[64:66]

        submit_time = datetime.datetime.now()
        lat = float(logstr[0:3]) + float(logstr[3:]) / 60000
        lng = float(latstr[0:3]) + float(latstr[3:]) / 60000
        speed = float(float(speedstr) / 3.6)
        bearing = int(dirstr)
        alerts = []

        B = int(Bstr, 16)
        if B&8 == 8:
            alerts.append(u'被拆除')

        data_time = submit_time

        try:
            data_time = datetime.datetime(int("20" + str(int(timestr[:2]))), int(timestr[2:4]), int(timestr[4:6]),
                                         int(timestr[6:8]), int(timestr[8:10]), int(timestr[10:12]))
        except Exception as ex:
            logging.debug("Wrong time format time=%s imei=%s", timestr, imei)
        return Location(
            imei=imei,
            time=data_time,
            lng=lng,
            lat=lat,
            speed=speed,
            bearing=bearing,
            altitude=0,
            alerts=alerts,
            jit=True,
        )

    def on_ms_89(self, s):
        ret = self.on_ms_80(s)
        ret.jit = False
        return ret

    def on_ms_d8(self, s):
        imei = A5.imei(s[10:18])
        return Identity(imei)


class Km(ProtocolTranslator):
    @staticmethod
    def imei(s):
        return s[10:22]
    @staticmethod
    def msg_munber(s):
        return s[22:26]
    @staticmethod
    def crc(s):
        f = None
        r = None
        for i in range(0, len(s), 2):
            c = int(s[i:i + 2], 16)
            if f == None:
                r = c
            else:
                r ^= c
            f = c
        return r
    @staticmethod
    def wrap(msg_id, imei, number, msg_body):
        msg_body_attrs = len(msg_body)&int('00000001111111111',2)
        body = '%s%s%s%s%s'%(msg_id, msg_body_attrs, imei, number, msg_body)
        crc = '%x' % Km.crc(body)
        r = '7e%s%s7e' % (body, crc)
        return r
    def main_signaling(self, s):
        return s[2:6]
    def on_main_signaling(self, ms, s):
        logging.debug('receive %s %s', ms, s)
    def on_ms_0100(self, s):
        # 7e010000210145304343740003002c012f37303131314b4d2d30312020203030303030303001d4c1423838383838437e
        #    消息ID[2:6] 消息体属性[6:10] 终端手机号[10:22] 消息流水号[22:26] 省域ID 市县域ID 制造商ID    终端型号            终端ID          车牌颜色  车牌
        # 7e 0100       0021           014530434374     0003            002c  012f    3730313131 4b4d2d3031202020  30303030303030 01       d4c1423838383838 43 7e

        imei = Km.imei(s)
        return Identity(imei)
    def on_ms_resp_0100(self, s):
        imei = Km.imei(s)
        num = Km.msg_munber(s)
        print '流水号', num
        #   消息头                       消息体            检验码
        #7e 8100 0021 014530434374 0000 [num 01 123456]  45    7e
        return Km.wrap(msg_id='8100', imei=imei, number='0000', msg_body=num+'01'+'123456')



