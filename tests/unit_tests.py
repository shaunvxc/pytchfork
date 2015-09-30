from pytchfork import _manage_work
from multiprocessing import Queue

work_queue = Queue()
done_queue = Queue()

def call(data):
    return True

def test_manage_work():

    work_queue.put("1")
    work_queue.put("done")

    _manage_work(call, work_queue, done_queue, "done")
    ct = 0

    while True:
        x = done_queue.get()
        if x == "done":
            break
        elif x is not None:
            ct = ct + 1

    assert ct == 1
