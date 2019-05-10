import logging
import random
from itertools import filterfalse
from typing import Optional

import discord
from discord import PermissionOverwrite

logger = logging.getLogger("banlab")


def get_justice_quote() -> str:
    quotes = ["Be nice and kind!", "Remember: my boxes and mazes are always ready! >:)",
              "I think, you don't want to meet me again :)", "You got off easy, don't you think?",
              "For your safety, do not do anything wrong!", "See you next time >:D"]
    return random.choice(quotes)


async def get_member(ctx, member) -> Optional[discord.Member]:
    if member is not None and ctx.guild.get_member_named(member) is not None:
        member = ctx.guild.get_member_named(member)
    elif member is not None:
        await ctx.send("{0} not found.".format(member))
        return None
    else:
        member = ctx.author
    if member == ctx.guild.me:
        await ctx.send("Nope :P You can't do this on me :D".format(member))
        return None
    return member


# noinspection PyUnresolvedReferences
async def trap(ctx, member, guild, exclude):
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
            await ctx.send("Warning! Something went wrong while trapping process! "
                           "Check if I have enough rights in {0.name}, especially "
                           "right to change permissions. Otherwise, the trap isn't"
                           " effective :(".format(channel))
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
