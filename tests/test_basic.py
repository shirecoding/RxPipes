from rxpipes import Pipeline

def test_basic():

    # create pipeline
    class Multiply(Pipeline):
        
        def setup(self, mul):
            self.mul = 2
        
        def run(self, x):
            return x * self.mul

    # execute a pipeline
    assert Multiply(2)(2) == 4
    assert Multiply(2)([1,2,3]) == [1, 2, 3, 1, 2, 3]