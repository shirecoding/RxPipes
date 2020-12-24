# RxPipes
A thin wrapper around RxPy for data-flow programming.

## Install

```bash
# install from git
git clone https://github.com/shirecoding/RxPipes.git
cd RxPipes
pip3 install ./
```

## Example: Static Data

```python
from rxpipes import Pipeline

# create pipeline
class Multiply(Pipeline):
    
    def setup(self, mul):
        self.mul = 2
    
    def operation(self, x):
        return x * self.mul

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

mul2 = Pipeline.from_lambda(lambda x: 2*x)
x = mul2(rx.interval(1), subscribe=lambda x: print(x)) # -> 0, 2, 4, 6, ....

x.dispose() # unsubscribe to observable
```

## Example: Parallel Processling

```python
import multiprocessing
from rx.scheduler import ThreadPoolScheduler

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
preprocessing = Pipeline.pipe(
    Rescale2D(50, 50),
    Normalize(0, 1),
    Pipeline.from_(lambda x: np.expand_dims(x, axis=-1))
)

postprocessing = Pipeline.pipe(
    Pipeline.from_(lambda x: np.argmax(x, axis=-1))
)

predict = Pipeline.pipe(
    preprocessing,
    Pipeline.from_(lambda x: model.predict(x)),
    postprocessing
)
```