# Quick Start

### Create a Custom Pipeline

```python
from rxpipes import Pipeline

class Multiply(Pipeline):

    def setup(self, mul):
        self.mul = 2

    def transform(self):
        from rx import operators as ops
        return ops.map(lambda x: x * self.mul)

# execute a pipeline
Multiply(2)(2) # -> 4
Multiply(2)([1,2,3]) # -> [2, 4, 6]
```

### Compose Pipelines

```python
mul2 = Multiply(2)
mul8 = mul2.pipe(
    mul2,
    mul2
)

mul8(2) # -> 16

# alternatively
mul8 = Pipeline.pipe(
    Multiply(2),
    Multiply(2),
    Multiply(2),
)(2)

mul8(2) # -> 16
```

### Create Pipeline from Lambda

```python

mul2 = Pipeline.map(lambda x: 2*x)

mul2(2) # -> 4
```

### Compatibility with Observables

```python
import rx
from rxpipes import Pipeline

mul2 = Pipeline.map(lambda x: 2*x)
x = mul2(rx.interval(1), subscribe=lambda x: print(x)) # -> 0, 2, 4, 6, ....

x.dispose() # unsubscribe to observable
```
