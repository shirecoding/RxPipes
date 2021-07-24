## Example: Reactive Data Streams

```python
import time
import rx
from rxpipes import Pipeline

mul2 = Pipeline.map(lambda x: 2*x)
x = mul2.to_observable(rx.interval(1)).subscribe(lambda x: print(x)) # -> 0, 2, 4, 6, ....

time.sleep(10)
x.dispose() # unsubscribe to observable
```
