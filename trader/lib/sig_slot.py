import asyncio


class SigSlot(object):

    def __init__(self):
        self._callbacks = list()

    def connect(self, func):
        if asyncio.iscoroutinefunction(func) and func not in self._callbacks:
            self._callbacks.append(func)

    def disconnect(self, func):
        if func in self._callbacks:
            self._callbacks.remove(func)

    async def emit(self, *args, **kwargs):
        for f in set(self._callbacks):
            await f(*args, **kwargs)
