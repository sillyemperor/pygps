# -*- coding:utf8 -*-
import pyodbc
import Queue

class GPSDal:
    def __init__(self, db_connections):
        self.location_buff = Queue.Queue(1024)
        self.db_connections = db_connections

    def fetchall(self, sql, *args):
        with pyodbc.connect(self.db_connections) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, *args)
                return cur.fetchall()

    def fetchone(self, sql, *args):
        with pyodbc.connect(self.db_connections) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, *args)
                return cur.fetchone()

    def execute(self, sql, *args):
        with pyodbc.connect(self.db_connections) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, *args)
                cur.commit()
                return cur.fetchone()

    def add_location(self, location):
        pass


