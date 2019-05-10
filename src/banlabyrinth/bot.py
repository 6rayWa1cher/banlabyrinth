import logging
from logging.handlers import RotatingFileHandler

from appdirs import *
from discord.ext import commands

from banlabyrinth import configmanager
from banlabyrinth.configmanager import CONFIG_PATH


def setup_logger():
    logs_path = configmanager.get_logs_path()
    if not os.path.exists(logs_path):
        os.mkdir(logs_path)
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(filename=logs_path + 'discord.log', encoding='utf-8', mode='w',
                                  maxBytes=8 * 1024 * 1024)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    logger = logging.getLogger('banlab')
    logger.setLevel(logging.INFO)
    handler1 = RotatingFileHandler(filename=logs_path + 'banlab.log', encoding='utf-8', mode='w',
                                   maxBytes=8 * 1024 * 1024)
    handler1.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    handler2 = logging.StreamHandler(stream=sys.stdout)
    handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler1)
    logger.addHandler(handler2)


def main():
    if not os.path.exists(CONFIG_PATH):
        configmanager.create_config()
    setup_logger()
    import banlabyrinth.dbmanager as dbmanager
    dbmanager.setup()
    token = configmanager.get_token()
    bot = commands.Bot(command_prefix=configmanager.get_command_prefix())
    bot.load_extension("banlabyrinth.cogs.roleregistrarcog")
    bot.load_extension("banlabyrinth.cogs.boxcog")
    bot.load_extension("banlabyrinth.cogs.trappedcog")
    logging.getLogger('banlab').info("Connecting...")
    bot.run(token)


if __name__ == '__main__':
    main()
