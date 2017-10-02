# -*- coding:utf8 -*-
"""博实结"""
from protocol import ProtocolTranslator
from result import Location, Identity
import datetime
import logging


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
    def getImei(s):
        return s[10:22]
    @staticmethod
    def getNum(s):
        return s[22:26]
    @staticmethod
    def mkCrc(s):
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
    def wrap(b):
        crc = '%x' % Km.mkCrc(b)
        r = '7e%s%s7e' % (b, crc)
        return r
    def main_signaling(self, s):
        return s[2:6]
    def on_main_signaling(self, ms, s):
        print ms, s
    def on_ms_0100(self, s):
        # 7e010000210145304343740003002c012f37303131314b4d2d30312020203030303030303001d4c1423838383838437e
        imei = Km.getImei(s)
        print imei
        return Identity(imei)
    def on_ms_resp_0100(self, s):
        num = Km.getNum(s)
        return Km.wrap('800100210145304343740000002c%s010000' % num)


