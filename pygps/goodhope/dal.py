# -*- coding:utf8 -*-

import logging
from functools import wraps


def reset_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        ex = None
        for i in  range(3):
            try:
                return f(*args, **kwds)
            except Exception as e:
                ex = e
                f.__self__.reset()
        if ex:
            raise ex
    return wrapper


# class Dummy:
#     def __init__(self):
#         self.r = False
#         self.fetchall = reset_decorator(self.fetchall)
#
#     def reset(self):
#         self.r = True
#
#     def fetchall(self, sql, *args):
#         print self.r
#         if not self.r:
#             raise Exception
#         return 'OK'
#
#
# d = Dummy()
#
# print d.fetchall("","")



import pyodbc

class GPSDal:
    def __init__(self, db_connections):
        self.location_buff = []
        self.db_connections = db_connections
        self.fetchall = reset_decorator(self.fetchall)
        self.fetchone = reset_decorator(self.fetchone)
        self.execute = reset_decorator(self.execute)

    def reset(self):
        logging.info('reset connection')
        try:
            self.conn.close()
        except Exception:
            pass
        delattr(self, 'conn')

    def get_conn(self):
        if not hasattr(self, 'conn'):
            self.conn = pyodbc.connect(self.db_connections)
        return self.conn

    def fetchall(self, sql, *args):
        conn = self.get_conn()
        cur = conn.cursor()
        try:
            cur.execute(sql, *args)
            return cur.fetchall()
        finally:
            cur.close()

    def fetchone(self, sql, *args):
        conn = self.get_conn()
        cur = conn.cursor()
        try:
            cur.execute(sql, *args)
            return cur.fetchone()
        finally:
            cur.close()

    def execute(self, sql, *args):
        conn = self.get_conn()
        cur = conn.cursor()
        try:
            cur.execute(sql, *args)
            conn.commit()
            return cur.rowcount
        finally:
            cur.close()

    def get_uid(self, imei):
        user = self.fetchone('''
                    select vehicleID, groupOwner from vehicle where IMEI=?;
                    ''', imei)
        if user:
            return user.vehicleID, user.groupOwner
        return None, None

    def add_location(self, location):
        vehicleID, groupOwner  = self.get_uid(location.imei)
        if not vehicleID:
            logging.error('Can`t found id match %s', location.imei)
            return

        position = 'POINT(%f %f)' % (location.lng, location.lat)

        if location.jit:
            print 'update vehicle', vehicleID, self.execute('''
            update [Vehicle] 
            set Mileage=?,
                position=geometry::STGeomFromText(?,4326),
                Speed=?,
                bearing =?,
                DataTime=?,
                SubmitTime=getdate(),
                ACC=?,
                Power=?,
                extension=? 
            where vehicleID=?;
            ''',
                         -1,
                         position,
                         location.speed,
                         location.bearing,
                         location.time,
                         location.acc,
                         location.power,
                         '',
                         vehicleID)
        self.treat_alert(vehicleID, groupOwner, location.alerts)
        self.location_buff.append((vehicleID, groupOwner, location))
        self.treat_buff()

    def treat_buff(self):
        n = len(self.location_buff)
        if n < 50:
            return

        self.treate_trace(n)

        self.location_buff = []

    def treat_alert(self, vehicleID, groupOwner, alerts):
        if not alerts:
            return
        n = len(alerts)
        if n<1:
            return
        values = ','.join(['(?, ?, ?)' for i in range(n)])
        params = []
        for a in alerts:
            params.append([a, groupOwner, vehicleID])
        print 'insert alert', len(params), self.execute('INSERT INTO Alert(Data,GroupOwner, VehicleID) VALUES {values}'.
                                                        format(values=values), *params)

    def treate_trace(self, n):
        values = ','.join(['''(?,?,geometry::STGeomFromText(?,4326),?,?,?,?,?,?,?,?,?,?)
            ''' for i in range(n)])
        params = []
        for vehicleID, groupOwner, location in self.location_buff:
            params.extend([
                vehicleID,
                "vehicle",
                'POINT(%f %f)' % (location.lng, location.lat),
                location.speed,
                location.bearing,
                location.time,
                location.submit_time,
                '',
                location.acc,
                location.power,
                -1,
                groupOwner,
                ''
            ])
        print 'insert tracepoint', len(params), self.execute('''
            INSERT INTO [Tracepoint]
			([SubjectID]
			,[SubjectType]
			,[Position]
			,[Speed]
			,[Bearing]
			,[DataTime]
			,[SubmitTime]
			,[Address]
			,[ACC]
			,[Power]
			,[Mileage]
			,[GroupOwner]
			,[Extension])
			VALUES {values}
            '''.format(values=values), *params)

    def get_all_signal(self, imei):
        for i in self.fetchall('''
        select 
            Instruction.InstructionID,
            Instruction.Sign,
            Instruction.Value 
        from Instruction,vehicle
        where 
            vehicle.imei = ? and 
            issend = 'false' and
            vehicle.vehicleid = Instruction.VehicleID        
        ''', imei):
            yield i.InstructionID, i.Sign

    def mark_read_signal(self, sid):
        self.execute('update instruction set SendDate=getdate(),IsSend=true where InstructionID=?', sid)

