# -*- coding:utf8 -*-
import Queue
from ..protocol.result import Location
import logging
import threading


class ThreadQueuePusher:
    def __init__(self, dal, maxsize=256):
        self.queue = Queue.Queue(maxsize=maxsize)
        self.dal = dal
        threading.Thread(target=self.poll_queue)

    def poll_queue(self):
        while True:
            o = self.queue.get()
            if isinstance(o, Location):
                try:
                    self.dal.add_location(o)
                except Exception as e:
                    logging.debug('failed to add_location %s %s', o, e)

    def push(self, o):
        try:
            self.queue.put_nowait(o)
        except Exception as e:
            logging.debug('failed to push %s %s', o, e)




