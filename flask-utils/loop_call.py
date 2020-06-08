# coding=utf-8
#

import logging
import time
from threading import Thread

log = logging.getLogger(__name__)
AsyncCall = None

"""
app = Flask()
init_async_call()

# 定期执行 task_worker_fn (每隔5秒钟)，可用于热加载之类的操作
task1 = LoopCall(task_worker_fn, 5)
task1.start(now=True)
"""


class _AsyncCall(Thread):

    def __init__(self, *args, **kwargs):
        self.tasks = set()
        super(_AsyncCall, self).__init__(*args, **kwargs)

    def register_task(self, task):
        if task not in self.tasks:
            self.tasks.add(task)

    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)

    def run(self):
        while True:
            now = time.time()
            for t in self.tasks:
                if t.exec_time > now:
                    continue

                try:
                    t.fn(*t.args)
                    t.exec_time = t.exec_time + t.interval
                except Exception as e:
                    log.error('async call error, fn: %s, err: %s' %
                              (t.fn.__name__, e))

            time.sleep(1)


def init_async_call():
    global AsyncCall
    AsyncCall = _AsyncCall()
    AsyncCall.daemon = True
    AsyncCall.start()


class LoopCall(object):
    def __init__(self, fn, interval, args=()):
        self.fn = fn
        self.args = args
        if not isinstance(interval, int):
            raise ValueError('LoopCall interval param expect int type')
        self.interval = interval
        self.exec_time = None

    def start(self, now=False):
        if now:
            self.fn(*self.args)

        self.exec_time = time.time()
        AsyncCall.register_task(self)

