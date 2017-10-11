# -*- coding:utf8 -*-
import pyodbc
import threading


class Pool:
    """Thread database connection pool"""
    def __init__(self, db_connections):
        self.db_connections = db_connections
        self.conn_cache = {}

    def get_conn(self):
        tid = threading.currentThread().ident
        if tid not in self.conn_cache:
            self.conn_cache[tid] = pyodbc.connect(self.db_connections)
        return self.conn_cache[tid]

    def fetchone(self, sql, args=()):
        conn = self.get_conn()
        cur = conn.cursor()
        try:
            cur.execute(sql, *args)
            return cur.fetchone()
        finally:
            cur.close()

    def execute(self, sql, args=()):
        conn = self.get_conn()
        cur = conn.cursor()
        try:
            cur.execute(sql, *args)
            conn.commit()
            return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()

    def fetchall(self, sql, args=()):
        conn = self.get_conn()
        cur = conn.cursor()
        try:
            cur.execute(sql, *args)
            return cur.fetchall()
        finally:
            cur.close()
