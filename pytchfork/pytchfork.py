# -*- coding: utf-8 -*-
from multiprocessing import Process, Pool
import functools

class pytchfork(object):

    def __init__(self, num_procs, work_queue=None, finished_queue=None, queue_sentinel=None, join=True):
        self.num_procs = num_procs
        self.procs = []
        self.work_queue = work_queue
        self.finished_queue = finished_queue
        self.queue_sentinel = queue_sentinel
        self.join = join
        self.manage_procs = work_queue is not None and finished_queue is not None and queue_sentinel is not None

    def __call__(self, f):
        def spawn_procs(*args):
            for x in range(0, self.num_procs):
                if self.manage_procs:
                    # target _manage_work to handle passing values to and from the work/finished queues
                    p = Process(target=_manage_work, args=(f, self.work_queue, self.finished_queue, self.queue_sentinel))
                else:
                    p = Process(target=f, args=(args))
                p.start()
                self.procs.append(p)

            if self.join:
                for proc in self.procs:
                    proc.join()

        functools.update_wrapper(spawn_procs, f)
        spawn_procs.__wrapped__ = f

        return spawn_procs

    def __enter__(self):
        self.pool = Pool(self.num_procs)
        return self.pool

    def __exit__(self, *args):
        self.pool.close()
        self.pool.join()
        self.pool.terminate()

''' manage a worker process '''
def _manage_work(f, work_queue, finished_queue, queue_sentinel):
    while True:
        work = work_queue.get()
        if work == queue_sentinel:
            finished_queue.put(queue_sentinel)
            break
        elif work is not None:
            finished_queue.put(f(work))
