import logging


class BaseStock:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.log = logging.getLogger(self.__class__.__name__)

    async def start(self):
        raise NotImplementedError()

    async def stop(self):
        raise NotImplementedError()

    def __getattr__(self, name):

        async def wrapper(*a, **kw):
            return await self.call_api(cmd=name, *a, **kw)

        return wrapper

    async def call_api(self, cmd, **payload):
        raise NotImplementedError()
