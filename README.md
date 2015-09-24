# pytchfork
Small library to decorate functions that should be run using python's multiprocessing module.  Currently a work in progress.

#Usage
You can easily mark methods to be run using multiple processes by invoking the pytchfork decorator:
###Decorator
```python
from pytchfork import pytchfork

@pytchfork(3)
def do_work(queue):
  data = queue.get()
  process(data)

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

