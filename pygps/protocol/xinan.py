# -*- coding:utf8 -*-
"""联和安业"""
from protocol import ProtocolTranslator
from result import Location, HeartBeat
import datetime
import logging


class Xinan(ProtocolTranslator):
    """
    T360-HE101GPRS、T360-HE269
                      SN          date time         lng            lat       speed  bearing   status
                     10            18                  30            38           46     50       54          60
                                                                                                                         alert
29 29 82 0023 10899f2d 141015112513    03018347  12005391  0000 0000   80 00 00 000800 0001000000 23 0d
29 29 82 0023 10899f2d 000000000000 00000000 00000000 0000 0000    00 00 00 000000 0000000000 8a 0d
29 29 82 0023 10899f2d 000000000000 00000000 00000000 0000 0000    00 00 00 000800 0001000000 83 0d
29 29 82 0023 10899f2d 000000000000 00000000 00000000 0000 0000    00 00 00 000800 0001000000 83 0d
值为1 表示报警，0 表示没有报警
alert 第一字节
~ D7 入区域报警
~ D6 出区域报警
~ D5 偏移路线报警
~ D4 低电压报警
~ D3
~ D2 自定义低
~ D1 自定义高
~ D0 非法启动

alert 第二字节
~ D7 非法开门
~ D6 拖车报警
~ D5 震动报警
~ D4 网关报警
~ D3 断电报警
~ D2 停车报警（停车超时）
~ D1 超速报警
~ D0 应急报警

alert 第三字节
~ D7 怠速报警（新增）即停车未熄火
~ D6 疲劳驾驶（新增）
~ D5 停车状态（新增）
~ D4 主机拆除报警（新增101A产品使用）
~ D3 主机GPRS流量报警
~ D2 温度异常
~ D1
~ D0

                     10            18                  30            38           46      50       54          60
29 29 80 0028 10899f2d 141015112501    03018347  12005391 00000 000f    80 00 44 2ffff5400001e00000000000045 0d
29 29 80 0028 10899f2d 000000000000 00000000 00000000 0000 0000     70 00 01  85ffff 5100001e00000000000038 0d

    """
    @staticmethod
    def sum(s):
        a = "00"
        for i in range(0, len(s), 2):
            tmp = (int(a, 16)) ^ (int(s[i:i + 2], 16))
            a = hex(tmp)[2:].zfill(2)
        return a

    @staticmethod
    def imei(ipstr):
        s1 = ipstr[0:2]
        i1 = int(s1, 16)
        s2 = ipstr[2:4]
        i2 = int(s2, 16) - 128
        s3 = ipstr[4:6]
        i3 = int(s3, 16) - 128
        s4 = ipstr[6:]
        i4 = int(s4, 16)
        imei = "136" + str(i1).zfill(2) + str(i2).zfill(2) + str(i3).zfill(2) + str(i4).zfill(2)
        return imei

    def main_signaling(self, value):
        return value[4:6]

    def build_response(self, value):
        res = "210005" + value[-4:-2] + value[4:6] + value[18:20]
        restr = "2929" + res + Xinan.sum(res) + "0d"
        return restr.upper()

    def on_ms_80(self, s):
        imei = Xinan.imei(s[10:18])
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

        accstr = bin(int(statusstr[0:2], 16))[2:].zfill(8)[0:1]
        ACC = 'off'
        if accstr == '0':
            ACC = 'ok'
        # print imei,accstr,statusstr,s
        gpsflat = "err"
        gpsstatus = "ok"
        powerstatus = "ok"
        dataTime = submitTime
        try:
            dataTime = datetime.datetime(int("20" + str(int(timestr[:2])))
                                         , int(timestr[2:4])
                                         , int(timestr[4:6])
                                         , int(timestr[6:8])
                                         , int(timestr[8:10])
                                         , int(timestr[10:12]))
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
                alerts=[],
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

    def on_ms_b1(self, s):
        imei = Xinan.imei(s[10:18])
        return HeartBeat(imei, datetime.datetime.now())

    def build_signal(self, name, s):
        ip = s[10:18]
        valstr = None
        if name == "turn on":
            valstr = "380006" + ip
        elif name == "shut down":
            valstr = "390006" + ip
        elif name == "call name":
            valstr = "300006" + ip
        elif name == "self check":
            valstr = "310006" + ip
        elif name == "reboot":
            valstr = "320006" + ip
        elif name == "cancel alarm":
            valstr = "370006" + ip
        if valstr:
            restr = "2929" + valstr + Xinan.sum(valstr) + "0d"
            return restr.upper()


