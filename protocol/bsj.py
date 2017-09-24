# -*- coding:utf8 -*-
"""博实结"""
from protocol import ProtocolTranslator
from result import Location
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
        restr = restr.upper()

    def on_ms_80(self, s):
        imei = A5.imei(s[10:18])
        # log
        timestr = s[18:30]
        logstr = s[30:38]
        latstr = s[38:46]
        speedstr = s[46:50]
        dirstr = s[50:54]
        statusstr = s[54:56]
        mileagestr = s[56:62]
        veicheStausstr = s[62:70]
        submitTime = datetime.datetime.now()
        lat = float(logstr[0:3]) + float(logstr[3:]) / 60000
        lng = float(latstr[0:3]) + float(latstr[3:]) / 60000
        speed = float(float(speedstr) / 3.6)
        bearing = int(dirstr)
        gpsflat = "err"
        gpsstatus = "ok"
        alerts = []

        a2 = int(statusstr, 16)
        powerstatus = (a2 & 0x1c == 0x14) and 'off' or 'on'
        if powerstatus == 'off':
            alerts.append(dict(description=u'断电'))

        dataTime = submitTime
        accstr = bin(int(statusstr[0:2], 16))[2:].zfill(8)[0:1]
        ACC = 'off'
        if accstr == '0':
            ACC = 'ok'
        try:
            dataTime = datetime.datetime(int("20" + str(int(timestr[:2]))), int(timestr[2:4]), int(timestr[4:6]),
                                         int(timestr[6:8]), int(timestr[8:10]), int(timestr[10:12]))
        except Exception as ex:
            logging.debug("Wrong time format time=%s imei=%s", timestr, imei)
        return Location(
            imei=imei,
            time=dataTime,
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
        ret = self.on_ms_80(s)
        ret.jit = False
        return ret


class Km(ProtocolTranslator):
    """KM"""
    pass

