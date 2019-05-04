import configparser
import logging
import os
import sys

from discord.ext import commands

import dbmanager

CONFIG_PATH = "../config.ini"
LOGS_PATH = "../logs/"


def create_config():
    config = configparser.ConfigParser()
    config["DEFAULT"]["token"] = "fill_me"
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)


def get_token():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if config["DEFAULT"]["token"] is None or config["DEFAULT"]["token"] == "fill_me":
        raise ValueError("Discord token not provided in \"{}\" !".format(os.path.abspath(CONFIG_PATH)))
    return config["DEFAULT"]["token"]


def setup_logger():
    if not os.path.exists(LOGS_PATH):
        os.mkdir(LOGS_PATH)
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=LOGS_PATH + 'discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    logger = logging.getLogger('banlab')
    logger.setLevel(logging.INFO)
    handler1 = logging.FileHandler(filename=LOGS_PATH + 'banlab.log', encoding='utf-8', mode='w')
    handler1.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    handler2 = logging.StreamHandler(stream=sys.stdout)
    handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler1)
    logger.addHandler(handler2)


if __name__ == '__main__':
    setup_logger()

    if not os.path.exists(CONFIG_PATH):
        create_config()
    dbmanager.setup()
    token = get_token()
    bot = commands.Bot(command_prefix='#')
    bot.load_extension("cogs.roleregistrarcog")
    bot.load_extension("cogs.boxcog")
    bot.load_extension("cogs.trappedcog")
    logging.getLogger('banlab').info("Connecting...")
    bot.run(token)
