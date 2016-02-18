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
        self.kwargz['read_from'] = read_from # work queue
        self.kwargz['write_to']  = write_to  # done queue
        self.kwargz['sentinel'] = sentinel
        self.kwargz['quiet'] = quiet
        if self.manage_redis: self.kwargz['redis_client'] = redis.StrictRedis(host=redis_uri, port=redis_port)

    def __call__(self, f):
        @wraps(f)
        def spawn_procs(*args, **kwargs):
            self.kwargz['passed_args'] = args
            self.kwargz['passed_kwargs'] = kwargs
            for x in range(0, self.num_procs):
                self._spawn_proc(f,x)

            for proc in self.procs: proc.join()

        return spawn_procs

    def _spawn_proc(self, f, pid):
        p = Process(target=_manage_worker, args=(f, pid), kwargs=self.kwargz)
        p.start()
        self.procs.append(p)

    def __enter__(self):
        self.pool = Pool(self.num_procs)
        return self.pool

    def __exit__(self, *args):
        self.pool.close()
        self.pool.join()
        self.pool.terminate()

def _manage_worker(*args, **kwargs):
    f, pid = args[0], args[1]
    logger = _get_logger('pytchfork.out'.format(f.__name__), pid, kwargs)

    if 'redis_client' in kwargs:
        _manage_redis(f, pid, **kwargs)
    elif kwargs['read_from']:
        _manage_work(f, pid, **kwargs)
    else:
        f(*kwargs['passed_args'], **kwargs['passed_kwargs'])

''' manage a worker process reading from a redis instance '''
def _manage_redis(f, pid, **kwargs):
    logger = _get_logger('pytchfork.out'.format(f.__name__), pid, kwargs)
    redis_client = kwargs['redis_client']
    read_from, write_to, sentinel = kwargs['read_from'], kwargs['write_to'], kwargs['sentinel']

    while True:
        work = redis_client.brpop(read_from)
        if sentinel and work[1] == sentinel:
            if write_to: redis_client.lpush(write_to, sentinel)
            logger.debug( "{}_{}: sentinel processed, closing...".format(f.__name__, pid))
            break
        elif work is not None:
            logger.debug( "{}_{}: processing `{}` ".format(f.__name__, pid, work[1]))
            res = f(work[1])
            if write_to: redis_client.lpush(write_to, res)


def _manage_work(f, pid, **kwargs):
    logger = _get_logger('pytchfork.out'.format(f.__name__), pid, kwargs)
    read_from, write_to, sentinel = kwargs['read_from'], kwargs['write_to'], kwargs['sentinel']

    while True:
        work = read_from.get()
        if sentinel and work == sentinel:
            if write_to: write_to.put(sentinel)
            logger.debug( "{}_{}: sentinel processed, closing...".format(f.__name__, pid))
            break
        elif work is not None:
            logger.debug( "{}_{}: processing `{}` ".format(f.__name__, pid, work))
            res = f(work)
            if write_to: write_to.put(res)


def _get_logger(name, pid, kwargs):
    mp_handler = multiprocessing_logging.MultiProcessingHandler('mp-handler', logging.FileHandler(name))
    logger = logging.Logger('pytchfork_{}'.format(pid))
    logger.addHandler(mp_handler)
    if kwargs['quiet']: logger.disabled = True
    return logger

def manage_redis(f, redis_client, work_queue, done_queue, sentinel):
    _manage_redis(f, 0, redis_client=redis_client, read_from=work_queue, write_to=done_queue, sentinel=sentinel, quiet=True)

def manage_work(f, work_queue, finished_queue, queue_sentinel):
    _manage_work(f, 0, read_from=work_queue, write_to=finished_queue, sentinel=queue_sentinel, quiet=True)
