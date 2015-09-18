# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division

from multiprocessing import Process

procs = []

def multiprocess(num_procs):    
    def wrap(f):
        def spawn_procs(*args):
            for x in range(0, num_procs): 
                p = Process(target=f, args=(args))
                p.start()

        return spawn_procs
    return wrap


@multiprocess(3)
def test():
    print "got here"

test()
