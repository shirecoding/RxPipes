# RxPipes
Framework for data-flow programming using RxPY

## Install

```bash
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
    
    def run(self, x):
        return x * self.mul

# execute a pipeline
Multiply(2)(2) # -> 4
Multiply(2)([1,2,3]) # -> [1, 2, 3, 1, 2, 3]

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
mul2 = Pipeline.from_(lambda x: 2*x)

mul2(2) # -> 4
```

## Example: Reactive Data Streams

```python
mul2 = Pipeline.pipe(
    Pipeline.from_(lambda x: 2*x),
    Pipeline.from_(print),
)

import rx
x = mul2(rx.interval(1), daemon=True) # -> 0, 2, 4, 6, ....
```

## Example: Parallel Processling

```python
mul2 = Pipeline.from_(lambda x: 2*x)

Pipeline.parallel(
    mul2,
    mul2
)(2, 4) # -> [4, 8]

import rx

Pipeline.parallel(
    mul2,
    mul2
)(rx.of(2, 4)) # -> [4, 8]
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