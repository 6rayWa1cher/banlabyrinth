import logging

import discord
from discord.ext import commands
from discord.utils import find

from banlabyrinth import dbmanager
from banlabyrinth.cogs.roleregistrarcog import is_role_powered
from banlabyrinth.utils import trap, untrap

logger = logging.getLogger("banlab")


class BoxCog(commands.Cog):
    """
    Commands to put somebody in very personal box.
    """

    def __init__(self, bot):
        self.bot = bot
        self.boxes = dict()

    @commands.command()
    @commands.check(is_role_powered)
    async def box(self, ctx, *, member: discord.Member = None):
        """
        Creates a box for the member and locks him in it.
        If member not provided, the effect will be on you!
        Requires "Labyrinth Keeper" role to be executed.
        Examples:
        #box Bad guy
        #box "Bad guy"
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
        if member.voice is not None:
            await member.move_to(channel)
        prev_member_roles = await trap(member, guild, {channel})
        dbmanager.push_box_member_roles(channel.id, prev_member_roles)
        self.boxes[(member, guild)] = channel
        logger.info("created personal box for {0.name} from guild {1.id}".format(member, guild))

    @commands.command()
    @commands.check(is_role_powered)
    async def unbox(self, ctx, *, member: discord.Member = None):
        """
        Removes the box and restores member permissions.
        Requires "Labyrinth Keeper" role to be executed.
        Examples:
        #unbox "Bad guy"
        #unbox Bad guy
        #unbox BadGuy
        """
        member = member or ctx.author
        guild = ctx.guild
        if (member, guild) not in self.boxes:
            box = find(lambda a: a.name == f"{str(member)}'s box", guild.voice_channels)
            if box is None:
                await ctx.send("Box for {0.display_name} not found.".format(member))
                return
        else:
            box = self.boxes[(member, guild)]
        await self._unbox(box, guild, member)

    async def _unbox(self, box, guild, member):
        await untrap(member, guild, dbmanager.get_box_member_roles(guild, box.id), {box})
        dbmanager.delete_box_member_roles(box.id)
        if (member, guild) in self.boxes:
            del self.boxes[(member, guild)]
        await box.delete(reason="Unboxing")
        logger.info("unboxed {0.name} from guild {1.id}".format(member, guild))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        after = after.channel
        if (member, guild) not in self.boxes:
            return
        if after is not None and after != self.boxes[(member, guild)]:
            await self._unbox(self.boxes[(member, guild)], guild, member)


def setup(bot):
    bot.add_cog(BoxCog(bot))
