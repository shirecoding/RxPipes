## Example: Reactive Data Streams

```python
import rx
from rxpipes import Pipeline

mul2 = Pipeline.from_lambda(lambda x: 2*x)
x = mul2(rx.interval(1), subscribe=lambda x: print(x)) # -> 0, 2, 4, 6, ....

x.dispose() # unsubscribe to observable
```