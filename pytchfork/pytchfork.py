# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from multiprocessing import Process, Pool
from functools import wraps

import redis
import logging
import multiprocessing_logging

logging.basicConfig(level=logging.DEBUG)
multiprocessing_logging.install_mp_handler()

class pytchfork(object):

    def __init__(self, num_procs, read_from=None, write_to=None, sentinel=None, redis_uri=None, redis_port=None, quiet=False):
        self.num_procs = num_procs
        self.procs = []
        self.manage_redis = read_from is not None and redis_uri is not None and redis_port is not None
        self.manage_procs = read_from is not None and sentinel is not None
        self.kwargz = {}
        self.kwargz['wq'] = read_from # work queue
        self.kwargz['dq'] = write_to  # done queue
        self.kwargz['sentinel'] = sentinel
        self.kwargz['quiet'] = quiet
        if self.manage_redis: self.kwargz['redis_client'] = redis.StrictRedis(host=redis_uri, port=redis_port)

    def __call__(self, f):
        @wraps(f)
        def spawn_procs(*args):
            for x in range(0, self.num_procs):
                target_fn, target_args, target_kwargs = self._get_target_and_args(f, args, pid=x)
                self._spawn_proc(target_fn, target_args, target_kwargs)

            for proc in self.procs: proc.join()

        return spawn_procs

    def _spawn_proc(self, fn, argz, kwargz):
        p = Process(target=fn, args=argz, kwargs=kwargz)
        p.start()
        self.procs.append(p)

    def _get_target_and_args(self, f, args, pid=0):
        self.kwargz['pid'] = pid
        if self.manage_redis:
            return _manage_redis, (f,), self.kwargz
        elif self.manage_procs:
            return _manage_work, (f,), self.kwargz
        else:
            return f, args, {}

    def __enter__(self):
        self.pool = Pool(self.num_procs)
        return self.pool

    def __exit__(self, *args):
        self.pool.close()
        self.pool.join()
        self.pool.terminate()


''' manage a worker process reading from a redis instance '''
def _manage_redis(f, **kwargs):

    redis_client = kwargs['redis_client']
    logger = _get_logger('pytchfork.out'.format(f.__name__), kwargs)

    while True:
        work = redis_client.brpop(kwargs['wq'])
        if work[1] == kwargs['sentinel']:
            if kwargs['dq']: redis_client.lpush(kwargs['dq'], kwargs['sentinel'])
            logger.debug( "{}_{}: sentinel processed, closing...".format(f.__name__, kwargs['pid']))
            break
        elif work is not None:
            logger.debug( "{}_{}: processing `{}` ".format(f.__name__, kwargs['pid'], work[1]))
            res = f(work[1])
            if kwargs['dq']: redis_client.lpush(kwargs['dq'], res)


def _manage_work(f, **kwargs):
    logger = _get_logger('pytchfork.out'.format(f.__name__), kwargs)

    while True:
        work = kwargs['wq'].get()
        if work == kwargs['sentinel']:
            if 'dq' in kwargs and kwargs['dq']: kwargs['dq'].put(kwargs['sentinel'])
            logger.debug( "{}_{}: sentinel processed, closing...".format(f.__name__, kwargs['pid']))
            break
        elif work is not None:
            logger.debug( "{}_{}: processing `{}` ".format(f.__name__, kwargs['pid'], work))
            res = f(work)
            if kwargs['dq']: kwargs['dq'].put(res)


def _get_logger(name, kwargs):
    mp_handler = multiprocessing_logging.MultiProcessingHandler('mp-handler', logging.FileHandler(name))
    logger = logging.Logger('pytchfork_{}'.format(kwargs['pid']))
    logger.addHandler(mp_handler)
    if kwargs['quiet']: logger.disabled = True
    return logger

def manage_redis(f, redis_client, work_queue, done_queue, sentinel):
    _manage_redis(f, redis_client=redis_client, wq=work_queue, dq=done_queue, sentinel=sentinel, quiet=True, pid=0)

def manage_work(f, work_queue, finished_queue, queue_sentinel):
    _manage_work(f, wq=work_queue, dq=finished_queue, sentinel=queue_sentinel, quiet=True, pid=0)
