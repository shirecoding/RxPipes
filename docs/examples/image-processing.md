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