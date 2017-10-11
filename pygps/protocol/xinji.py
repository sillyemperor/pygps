# -*- coding:utf8 -*-
from protocol import ProtocolTranslator
from result import Location, HeartBeat
import datetime
import logging


class Xinji(ProtocolTranslator):
    def main_signaling(self, value):
        return "80"

    def decode_data(self, data):
        s = ""
        for i in range(0, len(data), 2):
            s += chr(int(data[i:i + 2], 16))
        return s

    def on_ms_80(self, s):
        retlis = s.split(';')
        if len(retlis) < 6:
            return
        lat = float(retlis[4][1:4]) + float("0." + retlis[4][5:]) * 100.0 / 60.0
        lng = float(retlis[3][1:4]) + float("0." + retlis[3][5:]) * 100.0 / 60.0
        datastr = retlis[1]
        timestr = retlis[2]
        submitTime = datetime.datetime.now()
        imei = retlis[0][1:7]
        # 以下的这些需要协议才能解析
        speed = float(float(retlis[5]) / 3.6)
        mileage = -1
        bearing = int(retlis[6][0:3])
        stalis = retlis[0].split('=')
        sta = stalis[1]
        ACC = 'off'
        if sta[2:3] == '1':
            ACC = 'ok'
        powerstatus = 'ok'
        dataTime = submitTime
        try:
            dataTime = datetime.datetime(int("20" + datastr[:2]),
                                         int(datastr[2:4]),
                                         int(datastr[4:6]),
                                         int(timestr[0:2]) + 8, # 它的UTC时间，少了八个小时，加上
                                         int(timestr[2:4]), int(timestr[4:6]))
        except Exception as ex:
            logging.error("DataTime timestr=%s imei=%s", datastr, imei)

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

    def on_ms_8e(self, s):
        return self.on_ms_80(s)
    def on_ms_82(self, s):
        return self.on_ms_80(s)
