from __future__ import unicode_literals
from pytchfork import pytchfork
from multiprocessing import Queue, Manager
import mock
import redis
import sys

NUM_PROCS = 2

work_queue = Queue()
done_queue = Queue()

redis_work_queue = "test_in"
redis_done_queue = "test_out"

if sys.version_info[0] == 3:
    sentinel = "done".encode("latin-1")
else:
    sentinel=  "done"

class Dummy():

    def __init__(self):
        self.a = 0

    @pytchfork(NUM_PROCS)
    def test_call(self, l, foo=1):
        l.append(foo)

    @pytchfork(NUM_PROCS, read_from=work_queue, write_to=done_queue, sentinel=sentinel, quiet=True)
    def test_process_data(data):
        return data

    @pytchfork(NUM_PROCS, read_from=work_queue, sentinel=sentinel)
    def test_worker_only():
        pass

    @pytchfork(NUM_PROCS, read_from=redis_work_queue, write_to=redis_done_queue, sentinel=sentinel, redis_uri='localhost', redis_port=6379)
    def test_redis_decorator(data):
        return data

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

def test_redis():

    # connect to redis
    client = redis.StrictRedis(host='localhost', port=6379) # decode_responses=True )

    # Load up test data
    for x in range(0, 100):
        client.lpush(redis_work_queue, x)

    # mark the end of the test data (although the processes CAN
    # be run as daemons)
    for x in range(0, NUM_PROCS):
        client.lpush(redis_work_queue, sentinel)
    # run decorated method
    Dummy().test_redis_decorator()

    # evaluate the results
    total_ct = sentinel_ct = 0
    while True:
        x = client.brpop(redis_done_queue)
        if x[1] == sentinel:
            sentinel_ct = sentinel_ct + 1
            if sentinel_ct == NUM_PROCS:
                break
        elif x[1] is not None:
            total_ct = total_ct + 1

    assert sentinel_ct == NUM_PROCS
    assert total_ct == 100
