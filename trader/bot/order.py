import logging
from decimal import Decimal

from trader.api import ApiError


class Type:
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP_LOSS = 'STOP_LOSS'
    STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    LIMIT_MAKER = 'LIMIT_MAKER'


class Status:
    NEW = 'NEW'
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    REJECTED = 'REJECTED'
    EXPIRED = 'EXPIRED'


class Side:
    SELL = 'SELL'
    BUY = 'BUY'


class TimeInForce:
    GTC = 'GTC'
    IOC = 'IOC'
    FOK = 'FOK'


class Order:

    def __init__(self, stock, name, **kw):
        self.stock = stock
        self.name = name
        self._parse_order(kw)

        self.log = logging.getLogger(
            'Order-{}[{}]'.format(self.name, self.side)
        )

    def _parse_order(self, kw):
        self.id = kw.pop('orderId', None)
        self.type = kw.pop('type', None)
        self.side = kw.pop('side', None)
        self.price = Decimal(kw.pop('price', 0))
        self.quantity = Decimal(kw.pop('origQty', 0))
        self.stop_price = Decimal(kw.pop('stopPrice', 0))
        self.create_time = kw.pop('time', None)


    async def create(self, side, type, price, quantity, **kw):
        # Создать ордер. (weight 1)

        kw.setdefault('timeInForce', TimeInForce.GTC)
        kw.setdefault('newOrderRespType', 'RESULT')
        kw.setdefault('recvWindow', 5000)
        # Создать ордер. (weight 1)
        try:
            res = await self.stock.createOrder(symbol=self.name,
                                               side=side,
                                               type=type,
                                               price=str(price),
                                               quantity=str(quantity),
                                                **kw)
        except ApiError as err:
            self.log.error('Error create order: %s[%s] - %s',
                           err.status, err.code, err.msg)
            return
        self._parse_order(res)
        return self

    async def cancel(self):
        # Отменить ордер. (weight 1)
        res = await self.stock.cancelOrder(symbol=self.name, orderId=self.id)
