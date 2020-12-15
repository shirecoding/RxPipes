import rx
from rx import operators as ops
from rxpipes import Pipeline

class ScheduleEach(Pipeline):
    
    def setup(self, operation, scheduler):
        self.scheduler = scheduler
        self.operation = operation
    
    def _operation(self):
        return rx.pipe(
            ops.flat_map(lambda x: rx.of(x).pipe(ops.map(self.operation), ops.subscribe_on(self.scheduler)))
        )