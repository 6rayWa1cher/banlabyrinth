import logging
from itertools import filterfalse

import discord

logger = logging.getLogger("banlab")


async def trap(member, exclude=None):
    if exclude is None:
        exclude = set()
    for channel in filterfalse(exclude.__contains__, member.guild.voice_channels):
        try:
            # noinspection PyUnresolvedReferences
            await channel.set_permissions(member, read_messages=False, connect=False)
            logger.debug(
                "changing {0.name}'s from guild {1.id} roles in channel {2.name} to {3}".format(member, member.guild,
                                                                                                channel, "False"))
        except discord.errors.Forbidden:
            pass


async def untrap(member, exclude=None):
    if exclude is None:
        exclude = set()
    for channel in filterfalse(exclude.__contains__, member.guild.voice_channels):
        try:
            # noinspection PyUnresolvedReferences
            await channel.set_permissions(member, read_messages=None, connect=None)
            logger.debug(
                "changing {0.name} from guild {1.id} roles in channel {2.name} to {3}".format(member, member.guild,
                                                                                              channel, "None"))
        except discord.errors.Forbidden:
            pass
