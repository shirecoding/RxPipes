import rx
from rx import operators as ops
from rx import Observable
from abc import abstractmethod
from toolz import compose
from .utils import class_or_instancemethod
import types

class Pipeline():

    ##############################################################################
    ## CREATION
    ##############################################################################
    
    def __init__(self, *args, **kwargs):
        
        # call user setup
        self.setup(*args, **kwargs)

    @class_or_instancemethod
    def pipe(cls, *pipelines):

        # add parent to pipelines if instanced
        if not isinstance(cls, type):
            pipelines = (cls, *pipelines)

        class _wrapper(Pipeline):

            def setup(self):
                pass
                
            def run(self, x):
                return compose(
                    *[ p.run for p in pipelines ][::-1]
                )(x)

        return _wrapper()

    @class_or_instancemethod
    def parallel(cls, *pipelines):

        class _wrapper(Pipeline):

            def setup(self):
                pass
                
            def run(self, *args):
                return NotImplementedError

            @property
            def operator(self):
                return NotImplementedError

            def observable(self, *args):
                return rx.concat(*[ rx.of(x).pipe(ops.map(p.run)) for p, x in zip(pipelines, args) ]).pipe(
                    ops.buffer_with_count(len(pipelines))
                )

        return _wrapper()

    @classmethod
    def from_(cls, p):

        if isinstance(p, types.FunctionType) or callable(p):

            class _wrapper(Pipeline):

                def setup(self):
                    pass
                    
                def run(self, x):
                    return p(x)

            return _wrapper()

        else:
            raise Exception(f"unsupported type {type(p)}")

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
    def run(self, *args, **kwargs):
        """
        main logic
        """
        raise NotImplementedError("Pipeline/run")   

    ##############################################################################
    ## USE
    ##############################################################################

    @property
    def operator(self):
        """
        return the rx operator instead of __call__
        """
        return ops.map(self.run)

    def observable(self, *x):
        """
        return the observable instead of __call__
        """
        return rx.of(*x).pipe(self.operator)

    def __call__(self, *x, daemon=False):
        """
        run and return the result
        """
        if len(x) == 1 and isinstance(x[0], Observable):
            if daemon:
                return x[0].pipe(self.operator).subscribe()
            else:
                return x[0].pipe(self.operator).run()
        else:
            return self.observable(*x).run()

    
    ##############################################################################
    ## HELPERS
    ##############################################################################

    
