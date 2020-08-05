import asyncio


class Scheduler:
    def __init__(self, loop):
        self.loop = loop

    async def _schedule(self, delay, task, **kwargs):
        await asyncio.sleep(delay)
        task(**kwargs)

    async def _schedule_repeating_task(self, delay, task, **kwargs):
        while True:
            await asyncio.sleep(delay)
            task(**kwargs)

    def schedule(self, delay, task, **kwargs):
        self.loop.create_task(self._schedule(delay, task, **kwargs))

    def schedule_repeating_task(self, delay, task, **kwargs):
        self.loop.create_task(self._schedule_repeating_task(delay, task, **kwargs))

    async def _async_schedule(self, delay, async_task, **kwargs):
        await asyncio.sleep(delay)
        await async_task(**kwargs)

    async def _async_schedule_repeating_task(self, delay, async_task, **kwargs):
        while True:
            await asyncio.sleep(delay)
            await async_task(**kwargs)

    def async_schedule(self, delay, async_task, **kwargs):
        self.loop.create_task(self._async_schedule(delay, async_task, **kwargs))
