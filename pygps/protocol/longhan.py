# -*- coding:utf8 -*-
"""深圳翰盛"""
from result import Location, HeartBeat
from datetime import datetime
import logging
from protocol import ProtocolTranslator


class Longhan16m(ProtocolTranslator):
    """LH-16Smart（16M）"""
    @staticmethod
    def sum(s):
        a = "00"
        for i in range(0, len(s), 2):
            tmp = (int(a, 16)) ^ (int(s[i:i + 2], 16))
            a = hex(tmp)[2:].zfill(2)
        return a

    @staticmethod
    def imei(ipstr):
        simstr = '1'
        ip1 = int(ipstr[0:2], 16)
        ip2 = int(ipstr[2:4], 16)
        ip3 = int(ipstr[4:6], 16)
        ip4 = int(ipstr[6:8], 16)
        ref = int('80', 16)
        tmpstr = ""
        if ip1 > ref:
            tmpstr = "1"
            ip1 = ip1 - ref
        else:
            tmpstr = "0"
        if ip2 > ref:
            tmpstr += "1"
            ip2 = ip2 - ref
        else:
            tmpstr += "0"
        if ip3 > ref:
            tmpstr += "1"
            ip3 = ip3 - ref
        else:
            tmpstr += "0"
        if ip4 > ref:
            tmpstr += "1"
            ip4 = ip4 - ref
        else:
            simstr += "0"
        tmpnum = int(tmpstr, 2)
        if tmpnum < 10:
            tmpnum = tmpnum + 30
        else:
            tmpnum + tmpnum + 30 + 16
        simstr = "1" + str(tmpnum) + str(ip1).zfill(2) + str(ip2).zfill(2) + str(ip3).zfill(2) + str(ip4).zfill(2)
        return simstr

    def main_signaling(self, value):
        return value[4:6]

    def build_response(self, value):
        res = "210005" + value[-4:-2] + value[4:6] + value[18:20]
        restr = "2929" + res + Longhan16m.sum(res) + "0d"
        return restr.upper()

    def on_ms_b1(self, s):
        imei = Longhan16m.imei(s[10:18])
        return HeartBeat(imei, datetime.now())

    def on_ms_80(self, s):
        imei = Longhan16m.imei(s[10:18])
        timestr = s[18:30]
        lngstr = s[30:38]
        latstr = s[38:46]
        speedstr = s[46:50]
        dirstr = s[50:54]
        statusstr = s[54:56]
        mileagestr = s[56:62]
        veicheStausstr = s[62:70]

        lat = float(lngstr[0:3]) + float(lngstr[3:]) / 60000
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

        accstr = bin(int(statusstr[0:2], 16))[2:].zfill(8)[0:1]
        ACC = 'off'
        if accstr == '0':
            ACC = 'ok'

        submit_time = datetime.now()
        data_time = submit_time
        try:
            data_time = datetime(int("20" + str(int(timestr[:2]))), int(timestr[2:4]), int(timestr[4:6]),
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

    def on_ms_81(self, s):
        return self.on_ms_80(s)

    def on_ms_82(self, s):
        return self.on_ms_80(s)

    def on_ms_83(self, s):
        return self.on_ms_80(s)

    def on_ms_8e(self, s):
        ret = self.on_ms_80(s)
        ret.jit = False
        return ret
