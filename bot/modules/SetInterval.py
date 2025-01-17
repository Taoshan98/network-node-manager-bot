import asyncio, traceback


class SetInterval:
    def __init__(self, helpers, interval, action, *action_args):
        self.helpers = helpers
        self.interval = interval
        self.action = action
        self.action_args = action_args
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        while self._running:
            try:
                if asyncio.iscoroutinefunction(self.action):
                    await self.action(*self.action_args)
                else:
                    self.action(*self.action_args)
            except Exception as e:
                self.helpers.write_log('error', f"{type(e).__name__} – {e}\n{traceback.format_exc()}")
                self._running = False
                break

            await asyncio.sleep(self.interval)

    def cancel(self):
        self._running = False
        self._task.cancel()
