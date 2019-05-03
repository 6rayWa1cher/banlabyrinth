import logging
from itertools import filterfalse

import discord

logger = logging.getLogger("banlab")


# noinspection PyUnresolvedReferences
async def trap(member, exclude=None):
    if exclude is None:
        exclude = set()
    previous_member_roles = dict()
    for channel in filterfalse(exclude.__contains__, member.guild.voice_channels):
        try:
            if member in channel.overwrites:
                special_perms = channel.overwrites[member]
                if special_perms.read_messages is not None or special_perms.connect is not None:
                    previous_member_roles[channel] = (special_perms.read_messages, special_perms.connect)
            await channel.set_permissions(member, read_messages=False, connect=False)
            logger.debug(
                "changing {0.name}'s from guild {1.id} roles in channel {2.name} to {3}".format(member, member.guild,
                                                                                                channel, "False"))
        except discord.errors.Forbidden:
            pass
    return previous_member_roles


async def untrap(member, prev_roles, exclude):
    if prev_roles is None:
        prev_roles = dict()
    if exclude is None:
        exclude = set()
    for channel in filterfalse(exclude.__contains__, member.guild.voice_channels):
        try:
            read_messages, connect = prev_roles[channel] if channel in prev_roles else (None, None)
            # noinspection PyUnresolvedReferences
            await channel.set_permissions(member, read_messages=read_messages, connect=connect)
            logger.debug("changing {0.name} from guild {1.id} roles in channel {2.name} "
                         "to read_messages={3}, connect={4}".format(member, member.guild, channel, read_messages,
                                                                    connect))
        except discord.errors.Forbidden:
            pass
