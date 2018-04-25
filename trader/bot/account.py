import logging
from decimal import Decimal
from collections import namedtuple

from trader.api import ApiError
from .pair import TradeConditionError


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
        await self.load_opened_orders()

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
        quantity = Decimal('500')


        try:
            # Корректируем объем в соответствии с условиями биржи
            quantity = pair.correct_quantity(quantity)
            notional = quantity * price

            # Выполняем проверки условий торговли по паре
            pair.check_quantity(quantity)   # объем
            pair.check_notional(notional)   # сумма сделки

            # Выставляем ордер
            self.log.info('%sING %s %s at the rate of %s per %s (total %s %s)',
                          side,
                          quantity, pair.quote, price, pair.base,
                          notional, pair.base)
            order = await self.create_order(pair.name, side, 'LIMIT',
                                            price, quantity)
            self.orders[order.id] = order
            self.log.info('NEW %s', order)
        except TradeConditionError as err:
            self.log.error('Invalid trade condition: %s', err)
        except ApiError as err:
            self.log.error('Error create order: %s[%s] - %s',
                           err.status, err.code, err.msg)

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

        return self.Order(id=res['orderId'],
                          pair=pair_name,
                          status=res['status'],
                          type=res['type'],
                          side=res['side'],
                          price=Decimal(res['price']),
                          quantity=Decimal(res['executedQty']),
                          stop_price=Decimal(kw.get('stopPrice', 0)),
                          time=res['transactTime'])

    async def load_opened_orders(self):
        orders = await self.stock.openOrders()
        for i in orders:
            order = self.Order(id=i['orderId'],
                               pair=i['symbol'],
                               status=i['status'],
                               type=i['type'],
                               side=i['side'],
                               price=i['price'],
                               quantity=i['origQty'],
                               stop_price=i['stopPrice'],
                               time=i['time'])
            self.orders[order.id] = order
            self.log.info('LOAD %s', order)
