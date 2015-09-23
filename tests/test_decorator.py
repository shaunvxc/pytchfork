from pytchfork import pytchfork
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
    data = Manager().list()
    Dummy().test_call(data)
    assert len(data) == NUM_PROCS


def test_context_manager():
    data  = [x for x in range(0, 100)]

    def fill_empty(x):
        assert len(x) == len(data)

    with pytchfork(NUM_PROCS) as forked:
        assert forked._processes == NUM_PROCS
        res = forked.map_async(process_data, data, callback= fill_empty)

def process_data(x):
    return x
