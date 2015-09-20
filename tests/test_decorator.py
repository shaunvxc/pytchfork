from pytchfork import pytchfork
import multiprocessing
from multiprocessing import Queue, Manager
import mock

NUM_PROCS = 2

class Dummy():

    def __init__(self):
        self.a = 0

    @pytchfork(NUM_PROCS)
    def test_call(self, l):
        l.append("1")


def test_decorated_calls():
    manager = Manager()
    data = manager.list()
    x = Dummy()
    x.test_call(data)
    assert len(data) == NUM_PROCS


test_decorated_calls()
