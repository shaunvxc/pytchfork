# pytchfork
[![Build Status](https://travis-ci.org/shaunvxc/pytchfork.svg?branch=master)](https://travis-ci.org/shaunvxc/pytchfork)
[![Coverage Status](https://coveralls.io/repos/shaunvxc/pytchfork/badge.svg?branch=master&service=github)](https://coveralls.io/github/shaunvxc/pytchfork)

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
it will take care of polling the queue and passing data to the workers.

```python
from pytchfork import pytchfork
from multiprocessing import Queue

@pytchfork(3, read_from=work_queue, write_to=done_queue, sentinel="DONE")
def process_data(data):
  processed_data = do_something(data)
  return processed_data

process_data() # this call will fork 3 processes that read from work_queue & write to done_queue.
```
####Redis
Pytchfork processes can also be configured to read from and write to Redis instances (currently only Redis Lists are supported).  To do so, simply pass the `redis_uri` and `redis_port` to the pytchfork decorator (In addition to string values Redis will use to key the `work_queue` and `done_queue`).  

```python
from pytchfork import pytchfork

@pytchfork(2, read_from="work_queue", write_to="done_queue", redis_uri='localhost', redis_port=6379)
def process_data(data):
  processed_data = do_something(data)
  return processed_data

process_data() # this will fork 2 processes that read from/write to a local redis instance   
```

In the above snippet, these processes will run continuously as daemons.  For smaller tasks with fixed amounts of input data, this might not be desirable.

To get the processes to exit upon completetion, pass the `sentinel` argument to the decorator. In order for this to work, the `redis_work_queue` must clearly mark the ending with `N` occurrences of the `sentinel`, where `N` is the desired number of processes. 

Below is an example (verbosity for clarity):

```python
from pytchfork import pytchfork
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

###Context Manager
You can also use the context manager to get hold of a multiprocessing.Pool object, without having to manage the lifecycle of the pool.  I.e.:

```python
from pytchfork import pytchfork
    ...
    with pytchfork(num_procs) as forked:
        res = forked.map_async(process_data, data, callback=callback)
```

This construct ensures that the worker processes will be closed, joined and terminated upon the completion of the code in the block. 

###Command Line
You can also call pytchfork from the command line to run any command across multiple processes. 

To run any command:

```console
$ pytchfork target_command [target_command_options] [num_procs] 
```

To run a python module/package:
```console
$ pytchfork -p your_target_module [python_target_options] [num_procs]
```

If the optional `num_procs` argument is not provided, 2 will be used as default.

## Contributing
1. Fork it ( https://github.com/shaunvxc/pytchfork/fork )
1. Create your feature branch (`git checkout -b new-feature`)
1. Commit your changes (`git commit -am 'Add some feature'`)
1. Run the tests (`make test`)
1. Push change to the branch (`git push origin new-feature`)
1. Create a Pull Request
