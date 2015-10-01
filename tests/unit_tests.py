from __future__ import unicode_literals
from pytchfork import manage_work, manage_redis
from multiprocessing import Queue
import redis

work_queue = Queue()
done_queue = Queue()

def call(data):
    return True

def test_manage_work():

    sentinel = "done"

    work_queue.put("1")
    work_queue.put(sentinel)

    manage_work(call, work_queue, done_queue, sentinel)
    done_queue_count = 0

    while True:
        x = done_queue.get()
        if x == sentinel:
            break
        elif x is not None:
            done_queue_count = done_queue_count + 1

    assert done_queue_count == 1


def test_manage_redis():

    work_queue_key = "work_queue"
    done_queue_key = "done_queue"
    sentinel = "done"

    client = redis.StrictRedis(host='localhost', port=6379)

    client.lpush(work_queue_key, "test")
    client.lpush(work_queue_key, "test")
    client.lpush(work_queue_key, sentinel)

    manage_redis(call, client, work_queue_key,done_queue_key, sentinel)
    done_queue_count = 0

    while True:
        x = client.brpop(done_queue_key)
        if x[1] == sentinel:
            break
        elif x is not None:
            done_queue_count = done_queue_count + 1

    assert done_queue_count == 2
