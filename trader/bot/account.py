import logging
from decimal import Decimal
from collections import namedtuple

from trader.api import ApiError


class Account:

    log = logging.getLogger('Account')
    Balance = namedtuple('Balance', ['free', 'locked'])
    Order = namedtuple('Order', ['id',
                                 'pair',
                                 'status',
                                 'type',
                                 'side',
                                 'price',
                                 'quantity',
                                 'stop_price',
                                 'time'])

    def __init__(self, stock):
        self.stock = stock
        self.info = None
        self.balances = {}
        self.orders = {}

    async def start(self):
        # Получаем информацию об аккаунте
        await self.update_account_info()
        # await self.load_opened_orders()

    async def update_account_info(self):
        self.info = await self.stock.account()

        self.log.info('BALANCE:')
        for i in self.info.pop('balances'):
            balance = self.Balance(Decimal(i['free']), Decimal(i['locked']))
            if balance.free or balance.locked:
                self.log.info('    %s: %s(%s)',
                              i['asset'], balance.free, balance.locked)
            self.balances[i['asset']] = balance

    async def on_trade_signal(self, pair, side, price):
        # Здесь код, который определяет количество
        quantity = Decimal('1')

        # Корректируем объем в соответствии с условиями биржи
        quantity = pair.correct_quantity(quantity)
        if pair.quantity_allowed(quantity):
            self.log.info('%sING %s %s at the rate of %s per %s (total %s %s)',
                          side,
                          quantity, pair.quote, price, pair.base,
                          quantity * price, pair.base)
            # И создаем ордер
            try:
                order = await self.create_order(pair.name, side, 'LIMIT',
                                                price, quantity)
                self.orders[order.id] = order
                self.log.info('DONE')
            except ApiError as err:
                self.log.error('Error create order: %s[%s] - %s',
                               err.status, err.code, err.msg)
        else:
            self.log.warning('Quantity %s not allowed', quantity)

    async def create_order(self, pair_name, side, type, price, volume, **kw):
        # Создать ордер. (weight 1)
        params = {
            'symbol': pair_name,
            'side': side,
            'type': type,
            'price': str(price),
            'quantity': str(volume),
        }
        kw.setdefault('timeInForce', 'GTC')
        kw.setdefault('newOrderRespType', 'RESULT')
        kw.setdefault('recvWindow', 5000)
        params.update(kw)
        res = await self.stock.createOrder(**params)

        return Order(id=res['orderId'],
                     pair=pair.name,
                     status=res['status'],
                     type=res['type'],
                     side=res['side'],
                     price=res['price'],
                     quantity=res['executedQty'],
                     stop_price=kw['stopPrice'],
                     time=res['transactTime'])

    async def load_opened_orders(self):
        orders = await self.stock.openOrders()
        for i in orders:
            order = Order(self.stock, **i)
