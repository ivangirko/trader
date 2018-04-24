from decimal import Decimal

from . import BaseIndicator


class MACD(BaseIndicator):

    async def start(self):
        await super().start()

        # res = await self.pair.depth(10)
        # self.log.info(res)

        # res = await self.pair.trades(10)
        # self.log.info(res)

        # res = await self.pair.trade_batch(54803097, 10)
        # self.log.info(res)

        # res = await self.pair.trade_agg(54803097, limit=10)
        # self.log.info(res)

        # res = await self.pair.candles('5m', 10)
        # for i in res:
        #     self.log.info(i)

        # res = await self.pair.statistic_24hr()
        # self.log.info(res)

        # res = await self.pair.price()
        # self.log.info(res)


        # signal = self.SIGNAL.BUY
        # price = Decimal('12.000001232')
        # self.log.info('%s signal(%s)', signal, price)
        # await self.TRADE.emit(signal, self, price)

    async def stop(self):
        await super().stop()
