import logging
from typing import Any, Callable, Iterable, Optional, Type

import rx
from rx import Observable, operators
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.subject import Subject

from .utils import class_or_instance_method

log = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, *args: Optional[Any], **kwargs: Optional[Any]):
        """Pipeline

        Args and kwargs will be forwarded to user defined setup

        Args:
            args: args passed to user defined setup
            kwargs: kwargs passed to user defined setup
        """

        # call user setup
        self.setup(*args, **kwargs)

    ##############################################################################
    ## OVERRIDE WHEN SUBCLASSING
    ##############################################################################

    def setup(self, *args: Optional[Any], **kwargs: Optional[Any]):
        """
        Override this setup function to implement custom functionality when subclassing Pipeline

        Args:
            args: user defined args
            kwargs: user defined kwards
        """

    def transform(self) -> Callable[[rx.typing.Observable], rx.typing.Observable]:
        """
        Override this transform function to implement custom functionality when subclassing Pipeline

        Returns:
            a function mapping an observable to another (default = lambda x: x)
        """
        return lambda x: x

    ##############################################################################
    ## INTERNALS
    ##############################################################################

    def _operation(self):
        return operators.pipe(self.transform())

    ##############################################################################
    ## USAGE
    ##############################################################################

    @class_or_instance_method
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

    def to_observable(self, *args):
        return rx.merge(
            *[
                x
                if isinstance(x, rx.core.typing.Observable)
                else rx.from_(x)
                if isinstance(x, Iterable)
                else rx.of(x)
                for x in args
            ]
        ).pipe(self._operation())

    def to_blocking(self, *args):
        return self.to_observable(*args).pipe(operators.to_list()).run()

    def __call__(self, *args):
        """
        Alias for to_blocking
        """

        return self.to_blocking(*args)


##############################################################################
## Inject operators
##############################################################################


def pipeline_from_operator_jit(
    op: Callable[[rx.typing.Observable], rx.typing.Observable]
):
    """
    Returns a function that when called returns a Pipeline instance which
    pipes the parent transform to the injected operator

    Args:
        op: rx operator

    Returns:
        function returning a just-in-time created Pipeline instance
    """

    @class_or_instance_method
    def _f(parent, *args, **kwargs):
        if not isinstance(parent, type):
            return type(
                "Pipeline",
                (Pipeline,),
                {
                    "transform": lambda _: rx.pipe(
                        parent.transform(), op(*args, **kwargs)
                    )
                },
            )()
        else:
            return type(
                "Pipeline",
                (Pipeline,),
                {"transform": lambda _: op(*args, **kwargs)},
            )()

    return _f


# inject operators into Pipeline class
for op in [
    x for x in dir(operators) if x[0] != "_" and x[0].islower() and x not in ["pipe"]
]:
    setattr(Pipeline, op, pipeline_from_operator_jit(getattr(operators, op)))
