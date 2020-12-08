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