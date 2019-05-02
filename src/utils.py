import logging
from itertools import filterfalse

import discord
from discord.utils import find

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


def is_role_powered(ctx):
    rl = find(lambda r: r.name == "Labyrinth Keeper", ctx.author.roles)
    return rl is not None


async def check_role_existence(ctx):
    if "Labyrinth Keeper" not in map(lambda x: x.name, ctx.guild.roles):
        print("creating role")
        return await ctx.guild.create_role(name="Labyrinth Keeper", permissions=discord.Permissions.none())
    else:
        return next(x for x in ctx.guild.roles if x.name == "Labyrinth Keeper")
