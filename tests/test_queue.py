from notify.queue import MAX_RETRIES, Job, JobQueue, JobState


class Boom(Exception):
    pass


class Permanent(Exception):
    retryable = False


def make_queue(handler, sleeps, jitter=0.5):
    async def sleep(seconds):
        sleeps.append(seconds)

    return JobQueue(handler, sleep=sleep, jitter=lambda: jitter, base_delay=1.0)


async def test_success_first_try():
    calls = []

    async def handler(job):
        calls.append(job.notification_id)

    q = make_queue(handler, [])
    q.put(Job("n1"))
    job = await q.run_one()
    assert job.state is JobState.DONE and job.attempts == 1
    assert calls == ["n1"]
    assert await q.run_one() is None


async def test_recovers_after_transient_failures():
    seen = {"n": 0}

    async def handler(job):
        seen["n"] += 1
        if seen["n"] < 3:
            raise Boom("flaky")

    sleeps = []
    q = make_queue(handler, sleeps)
    q.put(Job("n1"))
    job = await q.run_one()
    assert job.state is JobState.DONE
    assert job.attempts == 3
    assert len(sleeps) == 2


async def test_dead_letters_after_max_retries():
    async def handler(job):
        raise Boom("always")

    sleeps = []
    q = make_queue(handler, sleeps)
    q.put(Job("n1"))
    job = await q.run_one()
    assert job.state is JobState.DEAD
    assert job.attempts == MAX_RETRIES + 1
    assert len(sleeps) == MAX_RETRIES
    assert job.last_error == "always"
    assert q.dead_letter == [job]


async def test_non_retryable_goes_straight_to_dead_letter():
    async def handler(job):
        raise Permanent("bad address")

    sleeps = []
    q = make_queue(handler, sleeps)
    q.put(Job("n1"))
    job = await q.run_one()
    assert job.state is JobState.DEAD and job.attempts == 1
    assert sleeps == []


def test_backoff_grows_and_jitter_scales():
    async def handler(job):
        pass

    low = make_queue(handler, [], jitter=0.0)
    high = make_queue(handler, [], jitter=0.99)
    assert low.backoff_delay(1) == 0.5
    assert low.backoff_delay(2) == 1.0
    assert low.backoff_delay(3) == 2.0
    assert high.backoff_delay(1) > low.backoff_delay(1)
    assert high.backoff_delay(1) < 1.5


async def test_drain_preserves_order():
    order = []

    async def handler(job):
        order.append(job.notification_id)

    q = make_queue(handler, [])
    for i in range(3):
        q.put(Job(f"n{i}"))
    finished = await q.drain()
    assert [j.notification_id for j in finished] == ["n0", "n1", "n2"]
    assert order == ["n0", "n1", "n2"]
    assert q.pending == 0
