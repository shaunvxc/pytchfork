from pytchfork import pytchfork
from multiprocessing import Queue, Manager
import mock

NUM_PROCS = 2

work_queue = Queue()
done_queue = Queue()
sentinel = "done"

class Dummy():

    def __init__(self):
        self.a = 0

    @pytchfork(NUM_PROCS)
    def test_call(self, l):
        l.append("1")

    @pytchfork(NUM_PROCS, work_queue, done_queue, sentinel)
    def test_process_data(data):
        return data

    @pytchfork(NUM_PROCS, work_queue, queue_sentinel=sentinel)
    def test_worker_only():
        pass

def test_decorated_calls():
    data = Manager().list()
    Dummy().test_call(data)
    assert len(data) == NUM_PROCS

def test_pytchfork_manage_work():
    # load up the test data
    for x in range(0, 100):
        work_queue.put(x)

    # mark the end
    for x in range(0, NUM_PROCS):
        work_queue.put(sentinel)

    # run the decorated method
    Dummy().test_process_data()

    # evaluate the results
    total_ct = sentinel_ct = 0
    while True:
        x = done_queue.get()
        if x == sentinel:
            sentinel_ct = sentinel_ct + 1
            if sentinel_ct == NUM_PROCS:
                break
        elif x is not None:
            total_ct = total_ct + 1

    assert sentinel_ct == NUM_PROCS # unfortunately redundant
    assert total_ct == 100

def test_pytchfork_manage_work_worker_only():
    # load up the test data-- in this case, just the sentinels!
    for x in range(0, NUM_PROCS):
        work_queue.put(sentinel)

    # call decorated method
    Dummy().test_worker_only()

    # ideally would like to assert that there are no active processes but am having trouble with this..
    # for now, hanging on a test run indicates a failure..

def test_context_manager():
    data  = [x for x in range(0, 100)]

    def fill_empty(x):
        assert len(x) == len(data)

    with pytchfork(NUM_PROCS) as forked:
        assert forked._processes == NUM_PROCS
        res = forked.map_async(process_data, data, callback= fill_empty)

def process_data(x):
    return x
