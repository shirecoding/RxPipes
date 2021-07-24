## Example: Parallel Processling

```python
import time
import multiprocessing
from rx.scheduler import ThreadPoolScheduler
from rxpipes.concurrency import Parallel

optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

def intense_calculation(value):
    time.sleep(1)
    return value

Multiply(1).pipe(
    Parallel(intense_calculation, pool_scheduler)
)([1,2,3,4,5,6])

# -> [[1,2,3,4,5,6]]
```
