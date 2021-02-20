import asyncio

from rx.scheduler.eventloop import AsyncIOScheduler

from rxpipes import Pipeline, async_iterable_to_observable


async def ticker(delay, to):
    """Yield numbers from 0 to `to` every `delay` seconds."""
    for i in range(to):
        yield i
        await asyncio.sleep(delay)


def main(loop):
    obs = async_iterable_to_observable(ticker(0.2, 10), loop)
    Pipeline.map(lambda x: 2 * x).map(lambda x: x * 2)(
        obs, subscribe=lambda x: print(x), scheduler=AsyncIOScheduler(loop=loop)
    )


loop = asyncio.get_event_loop()

main(loop)

loop.run_forever()
