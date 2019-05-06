import logging
from itertools import filterfalse

import discord
from discord import PermissionOverwrite

logger = logging.getLogger("banlab")


# noinspection PyUnresolvedReferences
async def trap(member, guild, exclude):
    previous_member_roles = dict()
    for channel in filterfalse(exclude.__contains__, guild.voice_channels):
        try:
            if member in channel.overwrites:
                special_perms = channel.overwrites[member]
                if not special_perms.is_empty():
                    previous_member_roles[channel] = special_perms.pair()
            await channel.set_permissions(member, read_messages=False, connect=False)
            logger.debug("changing {0.name} from guild {1.id} roles in channel {2.name} "
                         "to read_messages={3}, connect={4}".format(member, guild, channel, "False",
                                                                    "False"))
        except discord.errors.Forbidden:
            pass
    return previous_member_roles


async def untrap(member, guild, prev_roles, exclude):
    for channel in filterfalse(exclude.__contains__, guild.voice_channels):
        try:
            special_perms = PermissionOverwrite.from_pair(*prev_roles[channel]) if channel in prev_roles \
                else PermissionOverwrite()
            # noinspection PyUnresolvedReferences
            await channel.set_permissions(member, overwrite=special_perms)
            logger.debug("changing {0.name} from guild {1.id} roles in channel {2.name} "
                         "to allow={3}, deny={4}".format(member, guild, channel, special_perms.pair()[0].value,
                                                         special_perms.pair()[1].value))
        except discord.errors.Forbidden:
            pass
