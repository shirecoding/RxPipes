import logging

import pytest
import rx

log = logging.getLogger(__name__)


@pytest.mark.report(
    specification="""
    """,
    procedure="""
    """,
    expected="""
    """,
)
def test_basic():
    """
    Basic tests
    """

    from rxpipes import Pipeline

    # create pipeline
    class Multiply(Pipeline):
        def setup(self, mul):
            self.mul = mul

        def transform(self):
            from rx import operators as ops

            return ops.map(lambda x: x * self.mul)

    # execute a pipeline
    assert Multiply(2)(2) == 4
    assert Multiply(2)([1, 2, 3]) == [2, 4, 6]
    assert Multiply(2).map(lambda x: 2 * x)(2) == 8
    assert Multiply(1).max()([1, 2, 3]) == [3]
    assert Multiply(2).map(lambda x: 2 * x).max()([1, 2, 3, 4, 5]) == [20]
    pipeline = Multiply(1).map(lambda x: 3 * x).filter(lambda x: x % 2 == 0).max()
    assert pipeline([1, 4, 2, 5, 2]) == [12]

    # subscribe to a pipeline
    acc = []
    Multiply(2)(rx.of(1, 2, 3), subscribe=lambda x: acc.append(x))
    assert acc == [2, 4, 6]
    acc = []
    pipeline = Multiply(1).map(lambda x: 3 * x).filter(lambda x: x % 2 == 0).max()
    pipeline(rx.from_([1, 4, 2, 5, 2]), subscribe=lambda x: acc.append(x))
    assert acc == [12]

    # compose pipelines from instance
    mul2 = Multiply(2)
    mul4 = mul2.pipe(mul2)
    assert mul4(2) == 8

    # compose pipelines from class
    assert Pipeline.pipe(mul2, mul2)(2) == 8
    assert Pipeline.pipe(Multiply(2), Multiply(2))(2) == 8

    # create pipeline from lambda
    assert Pipeline.map(lambda x: x * 2)(2) == 4

    # test buffer
    res = []
    Multiply(2).buffer_with_count(3).map(lambda xs: len(xs))(
        rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
        subscribe=lambda x: res.append(x),
    )
    assert res == [3, 3, 3, 3, 2]


@pytest.mark.report(
    specification="""
    """,
    procedure="""
    """,
    expected="""
    """,
)
def test_intermediate():
    """
    Intermediate tests
    """

    import numpy as np

    from rxpipes import Pipeline

    class Normalize(Pipeline):
        def setup(self, low, high):
            self.low = low
            self.high = high

        def transform(self):
            from rx import operators as ops

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
            import cv2
            from rx import operators as ops

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
