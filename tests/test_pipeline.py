import logging

import numpy as np
import pytest
import rx

from rxpipes import Pipeline

log = logging.getLogger(__name__)

# create pipeline
class Multiply(Pipeline):
    def setup(self, mul):
        self.mul = mul

    def transform(self):
        from rx import operators as ops

        return ops.map(lambda x: x * self.mul)


@pytest.mark.report(
    specification="""
    """,
    procedure="""
    """,
    expected="""
    """,
)
def test_pipeline_creation():
    """
    Basic tests
    """

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
def test_return_observable():

    Multiply(2)(2, return_observable=True).run() == Multiply(2)(2)


@pytest.mark.report(
    specification="""
    """,
    procedure="""
    """,
    expected="""
    1. if input is singular and non iterable, output is a singular
    2. if input is singular and iterable, the pipeline is applied to each element along the 1st dimension and appended to a list
    3. if there are multiple inputs, the pipeline is applied to each input seperately and appended to a list
    """,
)
def test_input_polymorphism():
    """
    Test input polymorphism
    """
    mul2 = Multiply(2)

    assert mul2(2) == 4
    assert mul2(2, 2) == [4, 4]
    assert mul2([2, 2]) == [4, 4]

    assert mul2([2], [2]) == [[2, 2], [2, 2]]
    assert mul2([[2], [2]]) == [[2, 2], [2, 2]]

    assert mul2(np.array([2])) == [4]
    assert mul2(np.array([2, 2])) == [4, 4]

    assert np.array_equal(mul2([np.array([2])])[0], np.array([4]))
    assert np.array_equal(mul2([np.array([2, 2])])[0], np.array([4, 4]))
