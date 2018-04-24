import yaml
import asyncio
import logging
import argparse

from trader.bot.bot_v1 import Bot_V1


def read_cfg(path):
    with open(path) as stream:
        return yaml.load(stream)


def run(cfg):
    bot = Bot_V1(cfg)

    try:
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(bot.start())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(bot.stop())
    finally:
        loop.close()


def main():
    logging.basicConfig(
        format='%(asctime)-15s %(levelname)-10s %(name)-30s %(message)s',
        level=logging.INFO
    )

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cfg', required=True, help='path to cfg.yaml')
    args = parser.parse_args()

    run(read_cfg(args.cfg))
