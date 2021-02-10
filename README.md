# RxPipes
A thin wrapper around RxPy for data-flow programming.

## Install

```bash
# install from git
git clone https://github.com/shirecoding/RxPipes.git
cd RxPipes
pip3 install ./

# install from pypi
pip install rxpipes
```

## Example: Static Data

```python
from rxpipes import Pipeline

# create pipeline
class Multiply(Pipeline):
    
    def setup(self, mul):
        self.mul = 2
    
    def transform(self):
        from rx import operators as ops
        return ops.map(lambda x: x * self.mul)

# execute a pipeline
Multiply(2)(2) # -> 4
Multiply(2)([1,2,3]) # -> [2, 4, 6]

# compose larger pipelines
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

# create pipeline from lamba
mul2 = Pipeline.from_lambda(lambda x: 2*x)

mul2(2) # -> 4
```

## Example: Reactive Data Streams

```python
import rx
from rxpipes import Pipeline

mul2 = Pipeline.from_lambda(lambda x: 2*x)
x = mul2(rx.interval(1), subscribe=lambda x: print(x)) # -> 0, 2, 4, 6, ....

x.dispose() # unsubscribe to observable
```

## Example: Parallel Processling

```python
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

## Example: Image Processing Pipeline

```python
from rxpipes import Pipeline
import numpy as np

class Normalize(Pipeline):

    def setup(self, low, high):
        self.low = low
        self.high = high

    def transform(self):
        from rx import operators as ops

        def _f(x):
            _max = x.max()
            _min = x.min()
            factor =  ((self.high - self.low) + 1e-12)/ ((_max - _min) + 1e-12)
            return (x - _min) * factor + self.low

        return ops.map(_f)

class Rescale(Pipeline):

    def setup(self, shape):
        self.shape = shape

    def transform(self):
        import cv2
        from rx import operators as ops
        
        def _f(x):
            return cv2.resize(x.astype('float32'), self.shape)

        return ops.map(_f)

p = Pipeline.pipe(
    Normalize(0,1),
    Rescale((3,3))
)
im = np.arange(5*5).reshape((5,5))

p(im)

# array([[0.08333334, 0.15277778, 0.22222222],
#        [0.43055555, 0.5       , 0.5694444 ],
#        [0.7777778 , 0.8472222 , 0.9166667 ]], dtype=float32)
```


