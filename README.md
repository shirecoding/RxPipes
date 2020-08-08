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

class Multiply(Pipeline):
    
    def setup(self, mul):
        self.mul = 2
    
    def run(self, x):
        return x * self.mul

Multiply(2)(2) # -> 4
Multiply(2)([1,2,3]) # -> [1, 2, 3, 1, 2, 3]
```