# -*- coding: utf-8 -*-
from multiprocessing import Process

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

        return spawn_procs
'''
def multiprocess(num_procs = 2):
    def wrap(f):
        def spawn_procs(*args):
            for x in range(0, num_procs):
                p = Process(target=f, args=(args))
                p.start()

        return spawn_procs
    return wrap
'''
