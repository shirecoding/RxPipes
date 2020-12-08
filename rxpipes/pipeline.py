import rx
from rx import operators
from rx import Observable
from abc import abstractmethod
from toolz import compose
from .utils import class_or_instancemethod
import types

# injectable_operations = [ x for x in dir(operators) if x[0] != '_' and x[0].islower() ]
injectable_operations = [ 'max', 'map' ]

class Pipeline():

    def __init__(self, *args, **kwargs):
        
        # inject operations
        for op in injectable_operations:
            parent = self
            # print(f"injecting Class_{op}, {getattr(operators, op)}")
            setattr(
                self,
                op,
                lambda *_args, **_kwargs: type(
                    f"Class_{op}",
                    (Pipeline,),
                    {'_operation': lambda self: rx.pipe(parent._operation(), getattr(operators, op)(*_args, **_kwargs))}
                )()
            )

        # print(dir(self))

        # call user setup
        self.setup(*args, **kwargs)

    ##############################################################################
    ## USER DEFINED METHODS
    ##############################################################################
    
    def setup(self, *args, **kwargs):
        pass

    def operation(self, *args, **kwargs):
        pass

    ##############################################################################
    ## INTERNALS
    ##############################################################################

    def _operation(self):
        return operators.map(self.operation)

    ##############################################################################
    ## USAGE
    ##############################################################################

    def __call__(self, *args):
        if len(args) == 1:
            if type(args[0]) in [list, tuple, set]:
                return rx.from_(args[0]).pipe(self._operation(), operators.to_list()).run()
            else:
                return rx.of(*args).pipe(self._operation()).run()
        else:
            return rx.of(*args).pipe(
                self._operation(),
                operators.to_list()
            ).run()

    def subscribe(self, *args, **kwargs):
        return self.obs.subscribe(*args, **kwargs)
