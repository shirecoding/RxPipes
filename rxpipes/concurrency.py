import rx
from rx import operators as ops

from rxpipes import Pipeline


class ScheduleEach(Pipeline):
    """
    Maps each element using operation on scheduler. Order is not preserved.
    """

    def setup(self, operation, scheduler):
        """"""
        self.scheduler = scheduler
        self.operation = operation

    def transform(self):
        return ops.flat_map(
            lambda x: rx.of(x).pipe(
                ops.map(self.operation), ops.subscribe_on(self.scheduler)
            )
        )


class Parallel(ScheduleEach):
    """
    Maps each element using operation on scheduler. Order is preserved.
    """

    def setup(self, operation, scheduler):
        """"""
        self.counter = 0

        def f(x):
            self.counter += 1
            return (self.counter, operation(x))

        super().setup(f, scheduler)

    def transform(self):
        return rx.pipe(
            super().transform(),
            ops.to_iterable(),
            ops.map(lambda xs: [y[1] for y in sorted(xs, key=lambda x: x[0])]),
        )
