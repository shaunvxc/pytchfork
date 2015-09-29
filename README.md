# pytchfork
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

@pytchfork(3, work_queue, finished_queue, queue_sentinel)
def process_data(data):
  processed_data = do_something(data)
  return processed_data

process_data() # this call will fork 3 processes that read from 
               # work_queue & write to finished_queue.
```

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
