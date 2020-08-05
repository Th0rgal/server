import asyncio


class Scheduler:
    def __init__(self, loop):
        self.loop = loop

    async def _schedule(self, task, delay):
        await asyncio.sleep(delay)
        task()

    async def _schedule_repeating_task(self, task, delay):
        while True:
            await asyncio.sleep(delay)
            task()

    def schedule(self, task, delay):
        self.loop.create_task(self._schedule(task, delay))

    def schedule_repeating_task(self, task, delay):
        self.loop.create_task(self._schedule_repeating_task(task, delay))

    async def _async_schedule(self, async_task, delay):
        await asyncio.sleep(delay)
        await async_task()

    async def _async_schedule_repeating_task(self, async_task, delay):
        while True:
            await asyncio.sleep(delay)
            await async_task()

    def async_schedule(self, async_task, delay):
        self.loop.create_task(self._async_schedule(async_task, delay))
