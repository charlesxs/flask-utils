# coding=utf-8
#

import logging
import time
import threading
from flask import Flask

log = logging.getLogger(__name__)

"""
app = Flask()
TaskManger.init_app(app)

# 定期执行 task_worker_fn (每隔5秒钟)，可用于热加载之类的操作
task1 = LoopCall(task_worker_fn, 5)
task1.start(now=True)
"""


class TaskManger:
    __instance = None

    __lock = threading.Lock()

    # 执行线程
    __ticker_thread = None

    # 标记类是否初始化完成
    init_done = False

    @classmethod
    def init_app(cls, app: Flask):
        """
        注意：此方法只需在入口执行一次
        :param app:
        :type app:
        :return:
        :rtype:
        """
        cls.__instance = cls()
        t = threading.Thread(target=cls.__instance.run, name='ticker_thread')
        t.setDaemon(True)
        t.start()
        cls.__ticker_thread = t
        app.task_manager = cls.__instance

    # 单例
    def __new__(cls, *args, **kwargs):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super(TaskManger, cls).__new__(cls)
            return cls.__instance

    def __init__(self):
        if TaskManger.init_done:
            return
        self.tasks = set()
        TaskManger.init_done = True

    def register_task(self, task):
        if task not in self.tasks:
            self.tasks.add(task)

    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)

    def run(self):
        while True:
            now = time.time()
            for t in self.tasks:  # type: LoopCall
                if t.get_next_time() > now:
                    continue

                try:
                    t.fn(*t.args)
                    t.calc_next_time()
                except Exception as e:
                    log.error('async call error, fn: %s, err: %s' %
                              (t.fn.__name__, e))

            time.sleep(1)

    def clear_tasks(self):
        self.tasks.clear()


class Task:
    def __init__(self, interval):
        if not isinstance(interval, int):
            raise ValueError('Task interval param expect int type')

        self.interval = interval
        self._next_exec_time = time.time() + interval

    def get_next_time(self):
        return self._next_exec_time

    def calc_next_time(self):
        self._next_exec_time += self.interval
        return self._next_exec_time


class LoopCall(Task):
    def __init__(self, fn, interval, args=()):
        super(LoopCall, self).__init__(interval)
        self.fn = fn
        self.args = args
        self.tm = TaskManger()

    def start(self, now=False):
        if now:
            self.fn(*self.args)

        self.tm.register_task(self)

