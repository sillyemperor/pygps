# -*- coding:utf8 -*-
import Queue
from ..protocol.result import Location
import logging
import threading
import traceback


class ThreadQueuePusher:
    def __init__(self, dal, maxsize=256):
        self.queue = Queue.Queue(maxsize=maxsize)
        self.dal = dal
        threading.Thread(target=self.poll_queue).start()

    def poll_queue(self):
        while True:
            o = self.queue.get()
            print 'poll_queue', self.queue.qsize()
            logging.debug('poll_queue size(%s)', self.queue.qsize())
            if isinstance(o, Location):
                try:
                    self.dal.add_location(o)
                except Exception as e:
                    logging.error('failed to add_location %s %s', o, e)
                    traceback.print_stack()

    def push(self, o):
        try:
            self.queue.put_nowait(o)
        except Exception as e:
            logging.error('failed to push %s %s', o, e)
            traceback.print_stack()




