import logging
import importlib

from .account import Account
from .pair import Pair

class Bot_V1:

    log = logging.getLogger('Bot_V1')

    def __init__(self, cfg):
        self.cfg = cfg
        self.stock = self.create_stock(**self.cfg['stock'])
        self.account = Account(self.stock)
        self.pairs = {}

        self.create_pairs(self.cfg['pairs'])

    @staticmethod
    def create_stock(cls, api_key, api_secret):
        module_path, cls_name = cls.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, cls_name)(api_key, api_secret)

    def create_pairs(self, pairs):
        for pair_props in pairs:
            pair = Pair(self.stock, **pair_props)
            pair.TRADE.connect(self.account.on_trade_signal)
            self.pairs[pair.name] = pair

    @staticmethod
    def get_pairs_info(pairs):
        res = {}
        for info in pairs:
            name = Pair.create_name(info['baseAsset'], info['quoteAsset'])
            res[name] = info
        return res

    async def start(self):
        await self.stock.start()
        await self.account.start()

        # Получаем инфу о торговых парах
        res = await self.stock.exchangeInfo()
        info = self.get_pairs_info(res['symbols'])

        for pair in self.pairs.values():
            await pair.start(info[pair.name])

    async def stop(self):
        for pair in self.pairs.values():
            await pair.stop()
