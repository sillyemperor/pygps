# -*- coding:utf8 -*-
import inspect


class Location:
    def __init__(self, imei, time, lng, lat, speed, bearing, altitude, alerts, jit):
        self.imei = imei
        self.time = time
        self.lng = lng
        self.lat = lat
        self.speed = speed
        self.bearing = bearing
        self.altitude = altitude
        self.alerts = alerts
        self.jit = jit

    def __str__(self):
        return ','.join([str(i) for i in inspect.getmembers(self)])


class HeartBeat:
    def __init__(self, imei, time):
        self.imei = imei
        self.time = time