import rx
from rx import operators
from rx import Observable
from abc import abstractmethod
from toolz import compose
from .utils import class_or_instancemethod
import types

class Pipeline():

    def __init__(self, *args, **kwargs):

        # inject operations
        def _make_operator_function(op):
            def f(*_args, **_kwargs):
                return self._create_operator_class(op, *_args, **_kwargs)
            return f
        for op in [ x for x in dir(operators) if x[0] != '_' and x[0].islower() ]:
            setattr(self, op, _make_operator_function(op))

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
            f"ParentPipelineInjected_{op}",
            (Pipeline,),
            {'_operation': lambda self: rx.pipe(parent._operation(), getattr(operators, op)(*args, **kwargs))}
        )()

    ##############################################################################
    ## USAGE
    ##############################################################################

    def __call__(self, *args, subscribe=None):
        if len(args) == 1 and type(args[0]) == Observable:
            if not subscribe:
                raise Exception("Error: subscribe kwargs is required when arg is an Observable")
            return args[0].subscribe(subscribe)
        elif len(args) == 1:
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
