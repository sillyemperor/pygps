# -*- coding:utf8 -*-
"""奇诺美"""
from protocol import ProtocolTranslator
from result import Location
import binascii
import datetime
eightHour=datetime.timedelta(hours=8)

class Qnm(ProtocolTranslator):
    def build_response(self, s, ms):
        pass

    def main_signaling(self, s):
        return s.startswith('24') and 'binary' or 'ascii'

    def decode_data(self, data):
        return data[0]=='$' and binascii.a2b_hex(data) or data

    def on_ms_binary(self, s):
        imei = s[2:12]
        hour = int(s[12:14])
        minute = int(s[14:16])
        second = int(s[16:18])
        day = int(s[18:20])
        month = int(s[20:22])
        year = 2000 + int(s[22:24])
        lat = float(s[24:26]) + float("%s.%s" % (s[26:28], s[28:32])) / 60.0
        lng = float(s[34:37]) + float("%s.%s" % (s[37:39], s[39:43])) / 60.0
        speed = float(s[44:47]) * 0.514  # 1 Knot=0.514 meters per second
        bearing = int(s[47:50])
        datatime = datetime.datetime(year, month, day, hour, minute, second) + eightHour
        status = s[50:58]
        alerts = []
        return Location(
            imei=imei,
            time=datatime,
            lng=lng,
            lat=lat,
            speed=speed,
            bearing=bearing,
            altitude=0,
            alerts=alerts,
            jit=True,
        )

    def on_ms_ascii(self, data):
        parts = data.split(',')
        if len(parts) != 13:
            print 'error', parts
            return False
        if parts[0][:1] != "*":
            print 'error', parts
            return False
        print 'ascii', parts
        flag = parts[4]
        imei = parts[1]
        lat = float(parts[5][0:2]) + float(parts[5][2:]) / 60.0
        lng = float(parts[7][0:3]) + float(parts[7][3:]) / 60.0
        if parts[6] == 'S':
            lat = -lat
        if parts[8] == 'W':
            lng = -lng
        time = parts[3]
        date = parts[11]
        hour = int(time[:2])
        minute = int(time[2:4])
        second = int(time[4:6])
        day = int(date[:2])
        month = int(date[2:4])
        year = 2000 + int(date[4:6])
        datatime = datetime.datetime(year, month, day, hour, minute, second) + eightHour
        print datatime
        status = parts[12]
        alerts = []
        return Location(
                    imei=imei,
                    time=datatime,
                    lng=lng,
                    lat=lat,
                    speed=0,
                    bearing=0,
                    altitude=0,
                    alerts=alerts,
                    jit=True,
                )



