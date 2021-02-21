import logging

import cv2
import numpy as np
import pytest
import rx
from rx import operators as ops

from rxpipes import Pipeline

log = logging.getLogger(__name__)


@pytest.mark.report(
    specification="""
    """,
    procedure="""
    """,
    expected="""
    """,
)
def test_normalize_rescale():
    """
    Intermediate tests
    """

    class Normalize(Pipeline):
        def setup(self, low, high):
            self.low = low
            self.high = high

        def transform(self):
            def _f(x):
                _max = x.max()
                _min = x.min()
                factor = ((self.high - self.low) + 1e-12) / ((_max - _min) + 1e-12)
                return (x - _min) * factor + self.low

            return ops.map(_f)

    ndarr = np.array([1, 2, 3])
    res = Normalize(0, 1)([ndarr])[0]
    assert res.min() >= 0
    assert res.max() <= 1 + 1e-12

    class Rescale(Pipeline):
        def setup(self, shape):
            self.shape = shape

        def transform(self):
            def _f(x):
                return cv2.resize(x.astype("float32"), self.shape)

            return ops.map(_f)

    ndarr = np.arange(64 * 64).reshape((64, 64))
    res = Rescale((32, 32))([ndarr])[0]
    assert res.shape == (32, 32)

    pipeline = Pipeline.pipe(Normalize(0, 1), Rescale((3, 3)))
    ndarr = np.arange(5 * 5).reshape((5, 5))
    res = pipeline([ndarr])[0]

    assert res.shape == (3, 3)
    assert res.min() >= 0
    assert res.max() <= 1 + 1e-12
