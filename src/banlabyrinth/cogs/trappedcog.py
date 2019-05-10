import logging
import re

import discord
from discord.ext import commands
from discord.utils import find

import banlabyrinth
from banlabyrinth import dbmanager
from banlabyrinth.cogs import roleregistrarcog
from banlabyrinth.cogs.roleregistrarcog import is_role_powered
from banlabyrinth.entities.labyrinth import Labyrinth, UP_ARROW, DOWN_ARROW, LEFT_ARROW, RIGHT_ARROW, CENTER_ICON
from banlabyrinth.lab import LabyrinthWalker, gen_lab
from banlabyrinth.utils import trap, untrap, get_justice_quote

logger = logging.getLogger("banlab")


class TrappedCog(commands.Cog):
    """
    Commands to put somebody in labyrinth.
    """

    def __init__(self, bot):
        self.bot = bot
        self._size_re = re.compile(r"^\d{1,2}x\d{1,2}$")
        self.channel_to_lab = None

    @commands.Cog.listener()
    async def on_ready(self):
        if self.channel_to_lab is None:
            logger.info("Connected to Discord API!")
            self.channel_to_lab = dbmanager.collect_data_from_db(self.bot)
            logger.info("Successfully decoded {} labyrinths from DB".format(len(self.channel_to_lab) // 5))

    @commands.command()
    @commands.check(is_role_powered)
    async def trap(self, ctx, member=None, size: str = "15x15"):
        """
        Creates a labyrinth for the member and locks him in it.
        If member not provided, the effect will be on you!
        Requires "Labyrinth Keeper" role to be executed.
        By default creates labyrinth 15x15 (thin walls). You can set another size (not square, for example):
        limits only 1 and 100 (both not inclusive) for both size.
        Examples:
        #trap "Bad guy"
        #trap "Bad guy" 20x15
        #trap BadGuy
        #trap BadGuy 25x50
        #trap BadGuy#1337
        """
        member = await banlabyrinth.utils.get_member(ctx, member)
        if member is None:
            return
        guild = ctx.guild
        if not self._size_re.fullmatch(size):
            await ctx.send("Incorrect sizes. NxM : 1 < N < 100 and 1 < M < 100")
            return
        lab_width, lab_height = map(int, size.split("x"))
        if lab_width <= 1 or lab_height <= 1:
            await ctx.send("Incorrect sizes. NxM : 1 < N < 100 and 1 < M < 100")
            return
        role = roleregistrarcog.get_role(self.bot, guild)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False,
                                                            create_instant_invite=False),
            member: discord.PermissionOverwrite(read_messages=True, connect=True, create_instant_invite=False),
            role: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, connect=True)
        }
        async with ctx.typing():
            folder = await guild.create_category_channel(f"{str(member)}'s labyrinth",
                                                         overwrites=overwrites)
            up = await folder.create_voice_channel(UP_ARROW, overwrites=overwrites)
            right = await folder.create_voice_channel(RIGHT_ARROW, overwrites=overwrites)
            center = await folder.create_voice_channel(CENTER_ICON, overwrites=overwrites)
            down = await folder.create_voice_channel(DOWN_ARROW, overwrites=overwrites)
            left = await folder.create_voice_channel(LEFT_ARROW, overwrites=overwrites)
            ls = gen_lab(lab_width, lab_height)
            lw = LabyrinthWalker(ls)
            lab = Labyrinth(lw, folder, None, up, right, down, left, center)
            try:
                await member.move_to(center)
            except discord.errors.HTTPException:
                pass
            previous_member_roles = await trap(ctx, member, guild, lab.channels)
            lab.previous_member_roles = previous_member_roles
            await lab.update_channels()
            self.channel_to_lab.update({i: lab for i in lab.channels})
            dbmanager.push_lab_to_db(lab)
            await ctx.send("{0.display_name} has been thrown into labyrinth >:)".format(member))
        logger.info("trapped {0.name} from guild {1.id} into labyrinth".format(member, guild))

    @commands.command()
    @commands.check(is_role_powered)
    async def pardon(self, ctx, *, member=None):
        """
        Removes the labyrinth and restores member permissions.
        Requires "Labyrinth Keeper" role to be executed.
        Examples:
        #pardon "Bad guy"
        #pardon Bad guy
        #pardon BadGuy
        """
        member = await banlabyrinth.utils.get_member(ctx, member)
        if member is None:
            return
        await self._pardon(member, ctx.guild)
        await ctx.send("Pardoned {0.display_name}. {1}".format(member, get_justice_quote()))
        logger.info("pardoned {0.name} from guild {1.id}".format(member, ctx.guild))

    async def _pardon(self, member: discord.Member, guild):
        folder = find(lambda a: a.name == f"{str(member)}'s labyrinth", guild.categories)
        if folder is None:
            return
        some_channel = next(iter(folder.channels))
        if some_channel in self.channel_to_lab:
            lab = self.channel_to_lab[some_channel]
            await untrap(member, guild, lab.previous_member_roles, folder.channels)
        else:
            await untrap(member, guild, dict(), folder.channels)
        for channel in folder.channels:
            await channel.delete()
            if channel in self.channel_to_lab:
                del self.channel_to_lab[channel]
        dbmanager.delete_lab_from_db(folder.id)
        await folder.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        before = before.channel
        after = after.channel
        guild = member.guild
        if before not in self.channel_to_lab and after not in self.channel_to_lab:
            return
        if after is None or (before is not None and before.guild != after.guild):
            return
        if before in self.channel_to_lab:
            lab = self.channel_to_lab[before]
        else:
            lab = self.channel_to_lab[after]
        if after not in self.channel_to_lab:
            await self._pardon(member, guild)
            if guild.system_channel is not None:
                await guild.system_channel.send(
                    r"Pardoned {0.display_name}, because he's run away (or someone helped him). ¯\_(ツ)_/¯".format(
                        member))
            return
        if after == lab.center:
            return
        if lab.is_wall(after):
            await member.move_to(lab.center)
            return
        direction = lab.channel_to_direction[after]
        pos_before = lab.lab.curr
        move_result = lab.lab.move_into(direction)
        pos_after = lab.lab.curr
        logger.debug(
            "lab for {0.name} from guild {1.id}: {2} -> {3}".format(member, guild, pos_before, pos_after))
        if lab.lab.is_win():
            await self._pardon(member, guild)
            if guild.system_channel is not None:
                await guild.system_channel.send(
                    "{0.display_name} completed my maze! {1}".format(member, get_justice_quote()))
        else:
            await member.move_to(lab.center)
            await lab.update_channels()
            dbmanager.update_lab_data_in_db(lab)


def setup(bot):
    bot.add_cog(TrappedCog(bot))
