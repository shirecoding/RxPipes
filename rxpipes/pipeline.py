import logging
import uuid
from abc import abstractmethod
from typing import Any, Callable, Iterable, Optional, Type

import rx
from rx import Observable, operators
from rx.subject import ReplaySubject, Subject
from toolz import compose

from .utils import class_or_instancemethod

log = logging.getLogger(__name__)


# def pipeline_from_operator_jit(op):
#     """
#     Returns a function, when called returns a Pipeline instance piping the parent transform
#     to the injected operator
#     """
#     @class_or_instancemethod
#     def _f(parent, *args, **kwargs):
#         if not isinstance(parent, type):
#             return type(
#                 "Pipeline",
#                 (type(parent),),
#                 {
#                     "transform": lambda _: rx.pipe(
#                         parent.transform(), op(*args, **kwargs)
#                     )
#                 },
#             )()
#         else:
#             return type(
#                 "Pipeline",
#                 (parent,),
#                 {
#                     "transform": lambda _: op(*args, **kwargs)
#                 },
#             )()
#     return _f


class Pipeline:

    # for op in [
    #     x
    #     for x in dir(operators)
    #     if x[0] != "_" and x[0].islower() and x not in ["pipe"]
    # ]:
    #     # setattr(
    #     #     Pipeline, op, pipeline_from_operator_jit(getattr(operators, op))
    #     # )
    #     op = pipeline_from_operator_jit(getattr(operators, op))

    # map = pipeline_from_operator_jit(getattr(operators, 'map'))

    def __init__(self, *args: Optional[Any], **kwargs: Optional[Any]):
        """
        Pipeline

        Args:
            args: args passed to user defined setup
            kwargs: kwargs passed to user defined setup
        """

        for op in [
            x
            for x in dir(operators)
            if x[0] != "_" and x[0].islower() and x not in ["pipe"]
        ]:
            setattr(
                self, op, self.pipeline_from_operator_jit(self, getattr(operators, op))
            )

        # call user setup
        self.setup(*args, **kwargs)

    def pipeline_from_operator_jit(self, parent, op):
        """
        Returns a function, when called returns a Pipeline instance piping the parent transform
        to the injected operator
        """

        def _f(*args, **kwargs):
            return type(
                "Pipeline",
                (Pipeline,),
                {
                    "transform": lambda _: rx.pipe(
                        parent.transform(), op(*args, **kwargs)
                    )
                },
            )()

        return _f

    ##############################################################################
    ## USER DEFINED METHODS
    ##############################################################################

    def setup(self, *args: Optional[Any], **kwargs: Optional[Any]):
        """
        Override this setup function to implement custom functionality when subclassing Pipeline

        Args:
            args: user defined args
            kwargs: user defined kwards
        """
        self.args = args
        self.kwargs = kwargs

    def transform(self) -> Callable[[rx.typing.Observable], rx.typing.Observable]:
        """
        Override this transform function to implement custom functionality when subclassing Pipeline

        Returns:
            a function mapping an observable to another
        """
        return

    ##############################################################################
    ## INTERNALS
    ##############################################################################

    def _operation(self):
        return operators.pipe(self.transform())

    ##############################################################################
    ## USAGE
    ##############################################################################

    @class_or_instancemethod
    def pipe(self, *pipelines: "Pipeline") -> "Pipeline":
        """

        Can be used as a class or instance method to create a new pipeline chain

        Args:
            pipelines: variable number of pipelines

        Returns:
            newly composed Pipeline instance
        """

        # called as instance method
        if not isinstance(self, type):
            parent = self
            return type(
                "Pipeline",
                (Pipeline,),
                {
                    "transform": lambda self: rx.pipe(
                        parent.transform(), *[p.transform() for p in pipelines]
                    )
                },
            )()

        # called as class method
        else:
            return type(
                "Pipeline",
                (Pipeline,),
                {
                    "transform": lambda self: rx.pipe(
                        *[p.transform() for p in pipelines]
                    )
                },
            )()

    @classmethod
    def from_operator(cls, op: str) -> Type["Pipeline"]:
        """
        Create a new Pipeline class based on existing rx.operators

        Usage:
            ```python
            Map = Pipeline.from_operator('map')
            Map(lambda x: 2*x)(2) # 4
            ```

        Args:
            op: string representation of an operator from rx.operators

        Returns:
            Pipeline class with transform method injected with op
        """

        return type(
            "Pipeline",
            (Pipeline,),
            {
                "transform": lambda self: getattr(operators, op)(
                    *self.args, **self.kwargs
                ),
            },
        )

    @classmethod
    def from_lambda(cls, f: Callable) -> "Pipeline":
        """
        Convenience method for creating a Pipeline from the map operator and instantiating it with function f

        Args:
            f: function for the map operator

        Returns:
            Pipeline instance with injected map operator in transform and instantiated with f
        """
        return cls.from_operator("map")(f)

    def __call__(
        self,
        *args,
        subscribe=None,
        error=lambda e: log.error(e),
        completed=lambda: log.debug("completed"),
    ):

        if len(args) == 1:
            # observable is passed in
            if isinstance(args[0], rx.core.typing.Observable):
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
            elif isinstance(args[0], Iterable):
                return (
                    rx.from_(args[0]).pipe(self._operation(), operators.to_list()).run()
                )
            # constant or others
            else:
                return rx.of(*args).pipe(self._operation()).run()
        else:
            # multiple constants or others
            return rx.of(*args).pipe(self._operation(), operators.to_list()).run()
