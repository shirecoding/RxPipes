import asyncio
import functools

import rx
import rx.operators as ops
from rx.core.notification import OnCompleted, OnError, OnNext
from rx.disposable import Disposable
from rx.scheduler.eventloop import AsyncIOScheduler, AsyncIOThreadSafeScheduler


class class_or_instance_method(classmethod):
    def __get__(self, instance, type_):
        descr_get = super().__get__ if instance is None else self.__func__.__get__
        return descr_get(instance, type_)


def async_iterable_to_observable(iter, loop):
    def on_subscribe(observer, scheduler):
        async def _aio_sub():
            try:
                async for i in iter:
                    observer.on_next(i)
                loop.call_soon(observer.on_completed)
            except Exception as e:
                loop.call_soon(functools.partial(observer.on_error, e))

        task = asyncio.ensure_future(_aio_sub(), loop=loop)
        return Disposable(lambda: task.cancel())

    return rx.create(on_subscribe)


def observable_to_async_queue(obs, loop):
    queue = asyncio.Queue()
    disposable = obs.subscribe(
        on_next=lambda x: loop.call_soon_threadsafe(queue.put_nowait, x),
        scheduler=AsyncIOScheduler(loop=loop),
    )
    return queue, disposable


async def observable_to_async_iterable(obs, loop):
    queue = asyncio.Queue()

    disposable = obs.pipe(ops.materialize()).subscribe(
        on_next=lambda x: loop.call_soon_threadsafe(queue.put_nowait, x),
        scheduler=AsyncIOScheduler(loop=loop),
    )

    while True:
        x = await queue.get()
        if isinstance(x, OnNext):
            yield x.value
            queue.task_done()
        elif isinstance(x, OnError):
            disposable.dispose()
            raise Exception(f"Observable OnError: {x.value}")
        else:
            disposable.dispose()
            break
