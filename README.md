# pytchfork
[![Build Status](https://travis-ci.org/shaunvxc/pytchfork.svg?branch=master)](https://travis-ci.org/shaunvxc/pytchfork)

Pytchfork simplifies working with python's multiprocessing package.  By abstracting away the common boilerplate associated with forking processes and managing queues, pytchfork will allow you to write cleaner and more readable multiprocessing code.

#Usage
###Decorator
You can easily mark methods to be run using multiple processes by invoking the pytchfork decorator:
```python
from pytchfork import pytchfork
from multiprocessing import Queue

@pytchfork(3)
def do_work(queue):
  data = queue.get()
  process(data)

queue = Queue()
...
do_work(queue) # this call will fork 3 processes
```
Pytchfork can also manage queues for worker processes.  Just provide the necessary references to the decorator and
it will take care of polling the queue to pass data to the worker processes.

```python
from pytchfork import pytchfork
from multiprocessing import Queue

@pytchfork(3, work_queue, done_queue, queue_sentinel)
def process_data(data):
  processed_data = do_something(data)
  return processed_data

process_data() # this call will fork 3 processes that read from work_queue & write to done_queue.
```
####Redis
Pytchfork processes can also be configured to read from and write to Redis instances (currently only Redis Lists are supported).  To do so, simply pass the `redis_uri` and `redis_port` to the pytchfork decorator (In addition to string values Redis will use to key the `work_queue` and `done_queue`).  

```python
from pytchform import pytchfork

@pytchfork(2, "work_queue", "done_queue", redis_uri='localhost', redis_port=6379)
def process_data(data):
  processed_data = do_something(data)
  return processed_data

process_data() # this will fork 2 processes that read from/write to a local redis instance   
```

In the above snippet, these processes will run continuously as daemons.  For more smaller tasks, this might not be desirable. 

To get the processes to exit upon completetion, pass the `sentinel` argument to the decorator. In order for this to work, the `redis_work_queue` must clearly mark the ending with `N` occurrences of the `sentinel`, where `N` is the desired number of processes. 

Below is an example (verbosity for clarity):

```python
from pytchform import pytchfork
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379)
fill_redis_with_work_tasks(redis_client, "work_queue")

num_procs = 2
sentinel = "DONE"
# mark ending here:
for x in range(0, num_procs):
  redis_client.lpush("work_queue", sentinel)

# provide the sentinel to the decorator
@pytchfork(num_procs, "work_queue", "done_queue", sentinel, redis_uri=uri, redis_port=port)
def process_data(data):
  processed_data = do_something(data)
  return processed_data

process_data() # this will fork 2 processes that read/write to redis. Each process will
               # exit upon dequeueing a sentinel value from the redis work queue
```
For further reference on this, see the `test_redis()` method in `tests/test_decorator.py`.

###Command Line
You can also call pytchfork from the command line to run your python modules & packages across multiple processes.

To run a module:
```console
$ pytchfork your_target_module (num_procs) 
```

For a package:
```console
$ pytchfork package_name package_target (num_procs)
```
If the optional `num_procs` argument is not provided, 2 will be used as default.

###Context Manager
You can also use the context manager to get hold of a multiprocessing.Pool object, without having to manage the lifecycle of the pool.  I.e.:

```python
from pytchfork import pytchfork
    ...
    with pytchfork(num_procs) as forked:
        res = forked.map_async(process_data, data, callback=callback)
```

This construct ensures that the worker processes will be closed, joined and terminated upon the completion of the code in the block. 
