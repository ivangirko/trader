import logging
from decimal import Decimal
from collections import namedtuple

from trader.lib.sig_slot import SigSlot
from trader.indicator import create_indicator


class TradeConditionError(Exception):
    pass


class Pair:

    INTERVAL = {
        '1m',
        '3m',
        '5m',
        '15m',
        '30m',
        '1h',
        '2h',
        '4h',
        '6h',
        '8h',
        '12h',
        '1d',
        '3d',
        '1w',
        '1M',
    }

    Candle = namedtuple('Candle', ['open_time',
                                   'open_price',
                                   'high_price',
                                   'low_price',
                                   'close_price',
                                   'volume',
                                   'close_time',
                                   'quote_asset_volume',
                                   'number_of_trades',
                                   'taker_buy_base_asset_volume',
                                   'taker_buy_quote_asset_volume',
                                   'ignore'])

    def __init__(self, stock, quote, base, indicators):
        self.stock = stock
        self.quote = quote
        self.base = base
        self.info = None
        self.indicators = {}
        self.TRADE = SigSlot()
        self.log = logging.getLogger(str(self))
        self.log.info('CREATED')
        self._create_indicators(indicators)

    @staticmethod
    def create_name(quote, base):
        return '{}{}'.format(quote, base)

    def __str__(self):
        return self.create_name(self.quote, self.base)

    @property
    def name(self):
        return str(self)

    @property
    def min_price(self):
        return Decimal(self.info['filters'][0]['minPrice'])

    @property
    def max_price(self):
        return Decimal(self.info['filters'][0]['maxPrice'])

    @property
    def min_quantity(self):
        return Decimal(self.info['filters'][1]['minQty'])

    @property
    def max_quantity(self):
        return Decimal(self.info['filters'][1]['maxQty'])

    @property
    def min_notional(self):
        return Decimal(self.info['filters'][2]['minNotional'])

    def _create_indicators(self, indicators):
        for indicator_name in indicators:
            indicator = create_indicator(indicator_name, self)
            indicator.TRADE.connect(self.on_trade_signal)
            self.indicators[indicator_name] = indicator

    def correct_price(self, price, ):
        # Кратность шагу
        price = price - price % Decimal(self.info['filters'][0]['tickSize'])
        # Точность по паре
        return Decimal('{price:0.{precision}f}'.format(
            price=price, precision=self.info['baseAssetPrecision']
        ))

    def correct_quantity(self, quantity):
        # Кратность шагу
        quantity = quantity - quantity % Decimal(self.info['filters'][1]['stepSize'])
        # Точность по паре
        return Decimal('{quantity:0.{precision}f}'.format(
            quantity=quantity, precision=self.info['baseAssetPrecision']
        ))

    def check_price(self, price):
        if price < self.min_price or price > self.max_price:
            raise TradeConditionError(
                'price {} has to between [{}-{}]'.format(
                    price, self.min_price, self.max_price
                )
            )

    def check_quantity(self, quantity):
        if quantity < self.min_quantity or quantity > self.max_quantity:
            raise TradeConditionError(
                'quantity {} has to be between [{}-{}]'.format(
                    quantity, self.min_quantity, self.max_quantity
                )
            )

    def check_notional(self, notional):
        if notional < self.min_notional:
            raise TradeConditionError(
                'notional {} has to be upper {}'.format(
                    notional, self.min_notional
                )
            )

    async def start(self, info):
        self.info = info
        for indicator in self.indicators.values():
            await indicator.start()

    async def stop(self):
        for indicator in self.indicators.values():
            await indicator.stop()

    async def on_trade_signal(self, indicator, side, price):
        try:
            price = self.correct_price(price)
            self.check_price(price)
            await self.TRADE.emit(self, side, price)
        except TradeConditionError as err:
            self.log.warning('Invalid price: %s', err)

    # Сдесь описано API
    async def depth(self, limit=100):
        # Стакан котировок (weight 1)
        return await self.stock.depth(symbol=self.name, limit=limit)

    async def trades(self, limit=500):
        # История последних сделок (weight 1).Данные от старого к молодому
        return await self.stock.trades(symbol=self.name, limit=limit)

    async def trade_batch(self, from_id=None, limit=500):
        # История сделок (weight 5). Данные возвращаются от старого к молодому
        return await self.stock.historicalTrades(symbol=self.name,
                                                 fromId=from_id,
                                                 limit=limit)

    async def trade_agg(self, from_id=None,
                        start_time=None, end_time=None, limit=500):
        # История сделок (weight 1). Данные возвращаются от старого к молодому
        payload = {'limit': limit}
        if isinstance(start_time, int):
            payload['startTime'] = start_time
        if isinstance(end_time, int):
            payload['endTime'] = end_time
        if start_time and end_time:
            # Интервал не должен превышать суток (ms)
            if end_time - start_time > 86400000:
                raise Exception('Too large interval')
            payload.pop('limit', None)

        return await self.stock.historicalTrades(symbol=self.name,
                                                 fromId=from_id,
                                                 **payload)

    async def candles(self, interval, limit=500,
                      start_time=None, end_time=None):
        # Полчение свечей. (weight 1)
        if interval not in self.INTERVAL:
            raise Exception('Invalid candle interval')
        payload = {'limit': limit, 'interval': interval}
        if isinstance(start_time, int):
            payload['startTime'] = start_time
        if isinstance(end_time, int):
            payload['endTime'] = end_time
        res = await self.stock.klines(symbol=self.name, **payload)
        return map(lambda x: self.Candle(*x), res)

    async def statistic_24hr(self):
        # Полчение статистика за 24 часа. (weight 1)
        return await self.stock.ticker24hr(symbol=self.name)

    async def price(self):
        # Последняя цена. (weight 1)
        res = await self.stock.tickerPrice(symbol=self.name)
        return Decimal(res['price'])
