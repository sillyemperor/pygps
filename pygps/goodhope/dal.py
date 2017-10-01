# -*- coding:utf8 -*-
import pyodbc
import logging


class GPSDal:
    def __init__(self, db_connections):
        self.location_buff = []
        self.db_connections = db_connections

    def get_conn(self):
        if hasattr(self, 'conn'):
            self.conn = pyodbc.connect(self.db_connections)
        return self.conn

    def fetchall(self, sql, *args):
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, *args)
            return cur.fetchall()

    def fetchone(self, sql, *args):
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, *args)
            return cur.fetchone()

    def execute(self, sql, *args):
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, *args)
            cur.commit()
            return cur.rowcount

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
        self.location_buff.append((vehicleID, groupOwner, location))
        self.treat_buff()

    def treat_buff(self):
        n = len(self.location_buff)
        if n < 50:
            return

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

        self.location_buff = []

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

