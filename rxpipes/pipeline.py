import rx
from rx import operators as ops
from abc import abstractmethod
from toolz import compose

class Pipeline():
    
    def __init__(self, *args, **kwargs):
        
        # call user setup
        self.setup(*args, **kwargs)

    ##############################################################################
    ## USER DEFINED METHODS
    ##############################################################################
    
    @abstractmethod
    def setup(self, *args, **kwargs):
        """
        allow runtime configuration in "run" using setup parameters
        """
        raise NotImplementedError("Pipeline/setup")
   
    @abstractmethod
    def run(self, x):
        """
        main logic
        """
        raise NotImplementedError("Pipeline/run")   
    
    ##############################################################################
    ## INSTANCE METHODS
    ##############################################################################
    
    @property
    def operator(self):
        return ops.map(self.run)
    
    def observable(self, x):
        """
        return the observable instead of __call__
        """
        return rx.of(x).pipe(self.operator)
    
    def __call__(self, x):
        """
        run the observable and return the result
        """
        return self.observable(x).run()
    
    def pipe(self, *pipelines):

        parent = self

        class _wrapper(Pipeline):

            def setup(self):
                pass
                
            def run(self, x):
                return compose(
                    *[ p.run for p in pipelines ][::-1]
                )(parent(x))

        return _wrapper()

        