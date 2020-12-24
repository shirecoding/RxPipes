import rx
from rxpipes import Pipeline
from rxpipes.concurrency import ScheduleEach, Parallel
from rx.scheduler import ThreadPoolScheduler
import multiprocessing
import time

optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

def intense_calculation(value):
    time.sleep(0.01)
    return value

def test_concurrency():

    # test ScheduleEach - use set as order is not preserved
    res = Pipeline.from_lambda(lambda x: x) \
    .pipe(ScheduleEach(intense_calculation, pool_scheduler)) \
    ([1,2,3,4,5,6,7,8,9,10,11,12,13,14])
    assert set(res) == {1,2,3,4,5,6,7,8,9,10,11,12,13,14}

    res = set()
    Pipeline.from_lambda(lambda x: x) \
    .pipe(ScheduleEach(intense_calculation, pool_scheduler)) \
    (rx.of(1,2,3,4,5,6,7,8,9,10,11,12,13,14), subscribe=lambda x: res.add(x))
    time.sleep(1)
    assert res == {1,2,3,4,5,6,7,8,9,10,11,12,13,14}

    # test Parallel - order is preserved
    res = Pipeline.from_lambda(lambda x: x) \
    .pipe(Parallel(intense_calculation, pool_scheduler)) \
    ([1,2,3,4,5,6,7,8,9,10,11,12,13,14])
    assert res[0] == [1,2,3,4,5,6,7,8,9,10,11,12,13,14]

    res = []
    Pipeline.from_lambda(lambda x: x) \
    .pipe(Parallel(intense_calculation, pool_scheduler)) \
    (rx.of(1,2,3,4,5,6,7,8,9,10,11,12,13,14), subscribe=lambda x: res.append(x))
    time.sleep(1)
    assert res[0] == [1,2,3,4,5,6,7,8,9,10,11,12,13,14]