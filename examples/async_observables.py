import asyncio
import threading
import time

import rx
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.subject import Subject

from rxpipes import Pipeline, async_iterable_to_observable, observable_to_async_iterable

# event loop
loop = asyncio.get_event_loop()
loop.set_debug(True)

# example pipeline
class Multiply(Pipeline):
    def setup(self, mul):
        self.mul = mul

    def transform(self):
        from rx import operators as ops

        return ops.map(lambda x: x * self.mul)


print(
    """
########################################################################
## test observable_to_async_iterable in main thread
########################################################################
"""
)


async def task(loop):
    gen = observable_to_async_iterable(Multiply(2).to_observable([1, 2, 3, 4]), loop)
    async for i in gen:
        print(i, threading.current_thread())

    print("done")


print(f"run loop in thread {threading.current_thread()}")
loop.run_until_complete(task(loop))

print(
    """
########################################################################
## test observable_to_async_iterable with observable on same thread
########################################################################
"""
)


async def task(loop):
    gen = observable_to_async_iterable(
        Multiply(2)
        .take(5)
        .do_action(lambda x: print("observable", x, threading.current_thread()))
        .to_observable(rx.interval(0.25)),
        loop,
    )
    async for i in gen:
        print(i, threading.current_thread())

    print("done")


print(f"run loop in thread {threading.current_thread()}")
loop.run_until_complete(task(loop))

print(
    """
########################################################################
## test observable_to_async_iterable with observable on diff thread
########################################################################
"""
)

s = Subject()


def emissions():
    while True:
        time.sleep(0.5)
        print(f"emiting on thread {threading.current_thread()}")
        # loop.call_soon_threadsafe(s.on_next, 999)
        s.on_next(999)


threading.Thread(target=emissions).start()


async def task(loop):

    obs = Pipeline().take(5).to_observable(s)
    gen = observable_to_async_iterable(obs, loop)

    async for i in gen:
        print(i, threading.current_thread())


print(f"run loop in thread {threading.current_thread()}")
loop.run_until_complete(task(loop))


print(
    """
########################################################################
## async_iterable_to_observable
########################################################################
"""
)


async def ticker(delay, to):
    for i in range(to):
        yield i
        await asyncio.sleep(delay)


def main(loop):
    obs = async_iterable_to_observable(ticker(0.2, 10), loop)
    Pipeline.map(lambda x: 2 * x).map(lambda x: x * 2).to_observable(obs).subscribe(
        lambda x: print(x), scheduler=AsyncIOScheduler(loop=loop)
    )


main(loop)

loop.run_forever()
