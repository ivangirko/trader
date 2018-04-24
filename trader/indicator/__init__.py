import logging
import importlib

from trader.lib.sig_slot import SigSlot


class BaseIndicator:

    class SIGNAL:
        BUY = 'BUY'
        SELL = 'SELL'

    def __init__(self, pair):
        self.pair = pair
        self.TRADE = SigSlot()
        self.log = logging.getLogger(str(self))
        self.log.info('CREATED')

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return '{}({})'.format(self.name, self.pair)

    async def start(self):
        self.log.info('STARTED')

    async def stop(self):
        self.log.info('STOPPED')


def create_indicator(indicator_name, pair):
    module = importlib.import_module(
        'trader.indicator.{}'.format(indicator_name.lower())
    )
    return getattr(module, indicator_name)(pair)
