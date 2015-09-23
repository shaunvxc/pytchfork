# -*- coding: utf-8 -*-
from multiprocessing import Process
import functools

class pytchfork(object):

    def __init__(self, num_procs, join=True):
        self.num_procs = num_procs
        self.join = join
        self.procs = []

    def __call__(self, f):
        def spawn_procs(*args):
            for x in range(0, self.num_procs):
                p = Process(target=f, args=(args))
                p.start()
                self.procs.append(p)

            if self.join:
                for proc in self.procs:
                    proc.join()

        functools.update_wrapper(spawn_procs, f)
        spawn_procs.__wrapped__ = f

        return spawn_procs
