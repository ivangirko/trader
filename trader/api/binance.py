import time
import hmac
import hashlib
import urllib.parse

import aiohttp

from . import BaseStock, ApiError


class Binance(BaseStock):
    api_url = 'https://api.binance.com'
    methods = {
        # public methods
        'ping':             {'url':'api/v1/ping', 'method': 'GET', 'private': False},
        'time':             {'url':'api/v1/time', 'method': 'GET', 'private': False},
        'exchangeInfo':     {'url':'api/v1/exchangeInfo', 'method': 'GET', 'private': False},
        'depth':            {'url': 'api/v1/depth', 'method': 'GET', 'private': False},
        'trades':           {'url': 'api/v1/trades', 'method': 'GET', 'private': False},
        'historicalTrades': {'url': 'api/v1/historicalTrades', 'method': 'GET', 'private': False},
        'aggTrades':        {'url': 'api/v1/aggTrades', 'method': 'GET', 'private': False},
        'klines':           {'url': 'api/v1/klines', 'method': 'GET', 'private': False},
        'ticker24hr':       {'url': 'api/v1/ticker/24hr', 'method': 'GET', 'private': False},
        'tickerPrice':      {'url': 'api/v3/ticker/price', 'method': 'GET', 'private': False},
        'tickerBookTicker': {'url': 'api/v3/ticker/bookTicker', 'method': 'GET', 'private': False},
        # private methods
        'createOrder':      {'url': 'api/v3/order', 'method': 'POST', 'private': True},
        'testOrder':        {'url': 'api/v3/order/test', 'method': 'POST', 'private': True},
        'orderInfo':        {'url': 'api/v3/order', 'method': 'GET', 'private': True},
        'cancelOrder':      {'url': 'api/v3/order', 'method': 'DELETE', 'private': True},
        'openOrders':       {'url': 'api/v3/openOrders', 'method': 'GET', 'private': True},
        'allOrders':        {'url': 'api/v3/allOrders', 'method': 'GET', 'private': True},
        'account':          {'url': 'api/v3/account', 'method': 'GET', 'private': True},
        'myTrades':         {'url': 'api/v3/myTrades', 'method': 'GET', 'private': True},
    }

    @property
    def timestamp(self):
        return round(time.time() * 1000) + self.time_delta

    def get_sign(self, payload):
        return hmac.new(key=bytearray(self.api_secret, encoding='utf-8'),
                        msg=urllib.parse.urlencode(payload).encode('utf-8'),
                        digestmod=hashlib.sha256).hexdigest()

    async def start(self):
        local_ms = round(time.time() * 1000)
        res = await self.time()
        self.time_delta = res['serverTime'] - local_ms
        self.log.info('Server time_delta = %s', self.time_delta)

    async def stop(self):
        pass

    async def call_api(self, cmd, **payload):
        api_url = '{}/{}'.format(self.api_url, self.methods[cmd]['url'])
        headers = {"X-MBX-APIKEY": self.api_key}

        if self.methods[cmd]['private']:
            payload.update({'timestamp': self.timestamp})
            payload.update({'signature':self.get_sign(payload)})

        async with aiohttp.ClientSession() as session:
            method = getattr(session, self.methods[cmd]['method'].lower())
            async with method(api_url,
                              params=payload, headers=headers) as resp:
                res = await resp.json()
                if resp.status != 200:
                    raise ApiError(status=resp.status, **res)
                return res
