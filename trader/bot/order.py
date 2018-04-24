import logging


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

    def __init__(self, stock, pair, **kw):
        self.stock = stock
        self.pair = pair
        self.kw = kw
        self.id = None
        self.log = logging.getLogger(
            'Order-{side}[{name}]'.format(name=self.pair.name, **kw)
        )

        # Все параметры могут быть переопределены
        self.kw.setdefault('type', Type.LIMIT)
        self.kw.setdefault('timeInForce', TimeInForce.GTC)
        self.kw.setdefault('newOrderRespType', 'RESULT')
        self.kw.setdefault('recvWindow', 5000)

    async def create(self):
        # Создать ордер. (weight 1)
        res = await self.stock.createOrder(symbol=self.pair.name, **self.kw)
        self.id = res['orderId']
        self.log.info('Order id %s', self.id)
        return self.id

    async def cancel(self):
        # Отменить ордер. (weight 1)
        res = await self.stock.cancelOrder(symbol=self.pair.name,
                                           orderId=self.id)
