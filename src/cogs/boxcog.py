import logging

import discord
from discord.ext import commands
from discord.utils import find

from cogs.roleregistrarcog import is_role_powered
from src.utils import trap, untrap

logger = logging.getLogger("banlab")


class BoxCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boxes = dict()

    @commands.command()
    @commands.check(is_role_powered)
    async def box(self, ctx, *, member: discord.Member = None):
        """
        Creates a box for member and cages member in it. If member not provided, the effect will be on you!
        """
        member = member or ctx.author
        guild = ctx.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
            member: discord.PermissionOverwrite(read_messages=True, connect=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, connect=True)
        }
        channel = await ctx.guild.create_voice_channel(f"{str(member)}'s box", overwrites=overwrites,
                                                       reason="boxing")
        await member.move_to(channel)
        await trap(member, {channel})
        self.boxes[member] = channel
        logger.info("created personal box for {0.name} from guild {1.id}".format(member, guild))

    @commands.command()
    @commands.check(is_role_powered)
    async def unbox(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        if member not in self.boxes:
            box = find(lambda a: a.name == f"{str(member)}'s box", ctx.guild.voice_channels)
            if box is None:
                await ctx.send("Box for {0.display_name} not found.".format(member))
                return
        else:
            box = self.boxes[member]
        await untrap(member, {box})
        await box.delete(reason="Unboxing")
        logger.info("unboxed {0.name} from guild {1.id}".format(member, member.guild))


def setup(bot):
    bot.add_cog(BoxCog(bot))
