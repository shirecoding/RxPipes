# RxPipes
Framework for data-flow programming using RxPY

## Install

```bash
git clone https://github.com/shirecoding/RxPipes.git
cd RxPipes
pip3 install ./
```

## Usage

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
```