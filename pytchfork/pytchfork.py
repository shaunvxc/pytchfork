# -*- coding: utf-8 -*-
from multiprocessing import Process, Pool
from functools import wraps
import redis

class pytchfork(object):

    def __init__(self, num_procs, work_queue=None, done_queue=None, sentinel=None, redis_uri=None, redis_port=None):
        self.num_procs = num_procs
        self.procs = []
        self.work_queue = work_queue
        self.done_queue = done_queue
        self.sentinel = sentinel
        self.manage_redis = work_queue is not None and redis_uri is not None and redis_port is not None
        self.redis_client = None if not self.manage_redis else redis.StrictRedis(host=redis_uri, port=redis_port)
        self.manage_procs = work_queue is not None and sentinel is not None

    def __call__(self, f):
        @wraps(f)
        def spawn_procs(*args):
            for x in range(0, self.num_procs):
                target_fn, target_args = self._get_target_and_args(f, args, pid=x)
                self._spawn_proc(target_fn, target_args)

            for proc in self.procs: proc.join()

        return spawn_procs

    def _spawn_proc(self, fn, argz):
        p = Process(target=fn, args = argz)
        p.start()
        self.procs.append(p)

    def _get_target_and_args(self, f, args, pid=None):
        if self.manage_redis
            return _manage_redis, (f, self.redis_client, self.work_queue, self.done_queue, self.sentinel, pid)
        elif self.manage_procs:
            return _manage_work,  (f, self.work_queue, self.done_queue, self.sentinel, pid)
        else:
            return f, args

    def __enter__(self):
        self.pool = Pool(self.num_procs)
        return self.pool

    def __exit__(self, *args):
        self.pool.close()
        self.pool.join()
        self.pool.terminate()

def manage_redis(f, redis_client, work_queue, done_queue, sentinel):
    _manage_redis(f, redis_client, work_queue, done_queue, sentinel)

def manage_work(f, work_queue, finished_queue, queue_sentinel):
    _manage_work(f, work_queue, finished_queue, queue_sentinel)

''' manage a worker process reading from a redis instance '''
def _manage_redis(f, redis_client, work_queue, done_queue, sentinel, pid=None, log=False):

    import sys
    sys.stdout = open('.{}_{}.out'.format(f.__name__, pid), 'w+')

    while True:
        work = redis_client.brpop(work_queue)
        if work[1] == sentinel:
            if done_queue: redis_client.lpush(done_queue, sentinel)
            print "{}_{}: sentinel processed, closing...".format(f.__name__, pid)
            break
        elif work is not None:
            print "{}_{}: processing `{}` ".format(f.__name__, pid, work[1])
            res = f(work[1])
            if done_queue: redis_client.lpush(done_queue, res)

''' manage a worker process '''
def _manage_work(f, work_queue, done_queue, sentinel, pid=0):

    import sys
    sys.stdout = open('.{}_{}.out'.format(f.__name__, pid), 'w++')

    while True:
        work = work_queue.get()
        if work == sentinel:
            if done_queue: done_queue.put(sentinel)
            print "{}_{}: sentinel processed, closing...".format(f.__name__, pid)
            break
        elif work is not None:
            print "{}_{}: processing `{}` ".format(f.__name__, pid, work)
            res = f(work)
            if done_queue: done_queue.put(res)
