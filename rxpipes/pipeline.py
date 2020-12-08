import rx
from rx import operators
from rx import Observable
from abc import abstractmethod
from toolz import compose
from .utils import class_or_instancemethod
import types

# injectable_operations = [ x for x in dir(operators) if x[0] != '_' and x[0].islower() ]
injectable_operations = [ 'map', 'max' ]

class Pipeline():

    def __init__(self, *args, **kwargs):

        # # inject operations - DOES NOT WORK, LAST OPERATION OVERWRITES EVERYTHING
        # for op in injectable_operations:
        #     setattr(
        #         self,
        #         op,
        #         lambda *_args, **_kwargs: self._create_operator_class(op, *_args, **_kwargs)
        #     )

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

    def _create_operator_class(self, op, *args, **kwargs):
        parent = self
        return type(
            f"Class_{op}",
            (Pipeline,),
            {'_operation': lambda self: rx.pipe(parent._operation(), getattr(operators, op)(*args, **kwargs))}
        )()

    ##############################################################################
    ## Extend
    ##############################################################################

    def map(self, *args, **kwargs):
        return self._create_operator_class('map', *args, **kwargs)

    def max(self, *args, **kwargs):
        return self._create_operator_class('max', *args, **kwargs)

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
