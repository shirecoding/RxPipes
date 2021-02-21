import asyncio

import rx
from rx.scheduler.eventloop import AsyncIOScheduler

from rxpipes import Pipeline, async_iterable_to_observable, observable_to_async_iterable

# event loop
loop = asyncio.get_event_loop()

# example pipeline
class Multiply(Pipeline):
    def setup(self, mul):
        self.mul = mul

    def transform(self):
        from rx import operators as ops

        return ops.map(lambda x: x * self.mul)


########################################################################
## observable_to_async_iterable
########################################################################


async def test_observable_to_async_iterable(loop):
    gen = observable_to_async_iterable(
        Multiply(2)([1, 2, 3, 4], return_observable=True), loop
    )
    async for i in gen:
        print(i)

    print("done")


loop.run_until_complete(test_observable_to_async_iterable(loop))

########################################################################
## async_iterable_to_observable
########################################################################


async def ticker(delay, to):
    for i in range(to):
        yield i
        await asyncio.sleep(delay)


def main(loop):
    obs = async_iterable_to_observable(ticker(0.2, 10), loop)
    Pipeline.map(lambda x: 2 * x).map(lambda x: x * 2)(
        obs, subscribe=lambda x: print(x), scheduler=AsyncIOScheduler(loop=loop)
    )


main(loop)

loop.run_forever()
