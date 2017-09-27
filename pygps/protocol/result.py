# -*- coding:utf8 -*-
import inspect
from datetime import datetime


class Location:
    def __init__(self, imei, time, lng, lat, speed, bearing, altitude, alerts, jit, submit_time=datetime.now(), acc='on', power='on'):
        self.imei = imei
        self.time = time
        self.lng = lng
        self.lat = lat
        self.speed = speed
        self.bearing = bearing
        self.altitude = altitude
        self.alerts = alerts
        self.jit = jit
        self.acc = acc
        self.power = power
        self.submit_time = submit_time

    def __str__(self):
        return 'imei={imei}, time={time}, lng={lng}, lat={lat}, speed={speed}' \
               ', bearing={bearing}, altitude={altitude}, alerts={alerts}, jit={jit}' \
               ', submit_time={submit_time}, acc={acc}, power={power}'.format(
            imei=self.imei, time=self.time, lng=self.lng, lat=self.lat, speed=self.speed, bearing=self.bearing,
            altitude=self.altitude, alerts=self.alerts, jit=self.jit,
            submit_time=self.submit_time, acc=self.acc, power=self.acc
        )


class HeartBeat:
    def __init__(self, imei, time):
        self.imei = imei
        self.time = time