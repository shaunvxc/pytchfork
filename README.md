# pytchfork
Small library to decorate functions that should be run using python's multiprocessing module.  Currently a work in progress.

#Usage
You can easily mark methods to be run using multiple processes by invoking the pytchfork decorator:

```python
from pytchfork import pytchfork

@pytchfork(3)
def do_work(queue):
  job = queue.get()
  process(job)
```

