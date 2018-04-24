import logging
from decimal import Decimal
from collections import namedtuple

from .order import Order


class Account:

    Balance = namedtuple('Balance', ['free', 'locked'])



    log = logging.getLogger('Account')

    def __init__(self, stock):
        self.stock = stock
        self.info = None
        self.balances = {}

    async def start(self):
        # Получаем информацию об аккаунте
        await self.update_account_info()

        res = await self.opened_orders()

        print (res)
    async def update_account_info(self):
        self.info = await self.stock.account()

        self.log.info('BALANCE:')
        for i in self.info.pop('balances'):
            balance = self.Balance(Decimal(i['free']), Decimal(i['locked']))
            if balance.free or balance.locked:
                self.log.info('    %s: %s(%s)',
                              i['asset'], balance.free, balance.locked)
            self.balances[i['asset']] = balance

    async def on_trade_signal(self, signal, pair, price):
        # Здесь код, который определяет количество
        volume = Decimal('1')

        # Корректируем объем в соответствии с условиями биржи
        volume = pair.correct_volume(volume)
        if pair.volume_allowed(volume):
            self.log.info('%sING %s %s at the rate of %s per %s (total %s %s)',
                          signal,
                          volume, pair.quote, price, pair.base,
                          volume * price, pair.base)
            # И создаем ордер
            await self.create_order(signal, pair, price, volume)
        else:
            self.log.warning('Volume %s not allowed', volume)

    async def create_order(self, signal, pair, price, volume, otype='LIMIT'):
        # Создать ордер. (weight 1)
        order = Order(self.stock, pair=pair, side=signal, type=otype,
                      price=str(price), quantity=str(volume))

        await order.create()
        return order

    async def opened_orders(self):
        # return await self.stock.openOrders()
        pass
