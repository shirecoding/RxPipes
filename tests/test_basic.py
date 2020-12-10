import rx
from rxpipes import Pipeline

def test_basic():

    # create pipeline
    class Multiply(Pipeline):
        
        def setup(self, mul):
            self.mul = mul
        
        def operation(self, x):
            return x * self.mul

    # execute a pipeline
    assert Multiply(2)(2) == 4
    assert Multiply(2)([1,2,3]) == [ 2, 4, 6 ]
    assert Multiply(2).map(lambda x: 2 * x)(2) == 8
    assert Multiply(1).max()([1,2,3]) == [3]
    assert Multiply(2).map(lambda x: 2 * x).max()([1,2,3,4,5]) == [20]
    pipeline = Multiply(1) \
        .map(lambda x: 3*x) \
        .filter(lambda x: x%2 == 0) \
        .max()
    assert pipeline([1,4,2,5,2]) == [12]

    # subscribe to a pipeline
    acc = []
    Multiply(2)(rx.of(1,2,3), subscribe=lambda x: acc.append(x))
    assert acc == [2,4,6]
    acc = []
    pipeline = Multiply(1) \
        .map(lambda x: 3*x) \
        .filter(lambda x: x%2 == 0) \
        .max()
    pipeline(rx.from_([1,4,2,5,2]), subscribe=lambda x: acc.append(x))
    assert acc == [12]

    # compose pipelines
    mul2 = Multiply(2)
    mul4 = mul2.pipe(mul2)
    assert mul4(2) == 8
