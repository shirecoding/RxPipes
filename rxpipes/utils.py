import asyncio
import functools

import rx
import rx.operators as ops
from rx.core.notification import OnCompleted, OnError, OnNext
from rx.disposable import Disposable
from rx.scheduler.eventloop import AsyncIOScheduler


class class_or_instancemethod(classmethod):
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


async def observable_to_async_iterable(obs, loop):
    queue = asyncio.Queue()

    def on_next(i):
        queue.put_nowait(i)

    disposable = obs.pipe(ops.materialize()).subscribe(
        on_next=on_next, scheduler=AsyncIOScheduler(loop=loop)
    )

    while True:
        i = await queue.get()
        if isinstance(i, OnNext):
            yield i.value
            queue.task_done()
        elif isinstance(i, OnError):
            disposable.dispose()
            raise (Exception(i.value))
        else:
            disposable.dispose()
            break
