import logging
import uuid
from abc import abstractmethod
from typing import Callable

import rx
from rx import Observable, operators
from rx.subject import ReplaySubject, Subject
from toolz import compose

from .utils import class_or_instancemethod

log = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, *args, **kwargs):

        # inject operations
        def _make_operator_function(op):
            def f(*_args, **_kwargs):
                return self._create_operator_class(op, *_args, **_kwargs)

            return f

        for op in [
            x
            for x in dir(operators)
            if x[0] != "_" and x[0].islower() and x not in ["pipe"]
        ]:
            setattr(self, op, _make_operator_function(op))

        # call user setup
        self.setup(*args, **kwargs)

    ##############################################################################
    ## USER DEFINED METHODS
    ##############################################################################

    def setup(self, *args, **kwargs):
        pass

    def transform(self, *args, **kwargs):
        pass

    ##############################################################################
    ## INTERNALS
    ##############################################################################

    def _operation(self):
        return operators.pipe(self.transform())

    def _create_operator_class(self, op, *args, **kwargs):
        parent = self
        return type(
            f"ParentPipelineInjected_{op}",
            (Pipeline,),
            {
                "_operation": lambda self: rx.pipe(
                    parent._operation(), getattr(operators, op)(*args, **kwargs)
                )
            },
        )()

    ##############################################################################
    ## USAGE
    ##############################################################################

    @class_or_instancemethod
    def pipe(self, *pipelines):

        # called as instance method
        if not isinstance(self, type):
            parent = self
            return type(
                f"Pipeline_{id(self)}",
                (Pipeline,),
                {
                    "_operation": lambda self: rx.pipe(
                        parent._operation(), *[p._operation() for p in pipelines]
                    )
                },
            )()

        # called as class method
        else:
            return type(
                f"Pipeline_{uuid.uuid4().hex}",
                (Pipeline,),
                {
                    "_operation": lambda self: rx.pipe(
                        *[p._operation() for p in pipelines]
                    )
                },
            )()

    @classmethod
    def from_lambda(cls, f):
        return type(
            f"Pipeline_{uuid.uuid4().hex}",
            (Pipeline,),
            {"_operation": lambda self: operators.map(f)},
        )()

    def __call__(
        self,
        *args,
        subscribe=None,
        error=lambda e: log.error(e),
        completed=lambda: log.info("completed"),
    ):

        if len(args) == 1:
            # observable is passed in
            if type(args[0]) in [Observable, Subject, ReplaySubject]:
                if not subscribe:
                    raise Exception(
                        "Error: subscribe kwargs is required when arg is an Observable"
                    )
                return (
                    args[0]
                    .pipe(self._operation())
                    .subscribe(
                        on_next=subscribe, on_error=error, on_completed=completed
                    )
                )
            # fixed length iterable is passed in
            elif type(args[0]) in [list, tuple, set]:
                return (
                    rx.from_(args[0]).pipe(self._operation(), operators.to_list()).run()
                )
            # constant or others
            else:
                return rx.of(*args).pipe(self._operation()).run()
        else:
            # multiple constants or others
            return rx.of(*args).pipe(self._operation(), operators.to_list()).run()
