import logging
import re

import discord
from discord.ext import commands
from discord.utils import find

import dbmanager
from cogs import roleregistrarcog
from cogs.roleregistrarcog import is_role_powered
from entities.labyrinth import Labyrinth, UP_ARROW, DOWN_ARROW, LEFT_ARROW, RIGHT_ARROW, CENTER_ICON
from src.lab import LabyrinthWalker, gen_lab
from src.utils import trap, untrap

logger = logging.getLogger("banlab")


class TrappedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._size_re = re.compile(r"^\d{1,2}x\d{1,2}$")
        self.channel_to_lab = None

    @commands.Cog.listener()
    async def on_ready(self):
        if self.channel_to_lab is None:
            self.channel_to_lab = dbmanager.collect_data_from_db(self.bot)

    @commands.command()
    @commands.check(is_role_powered)
    async def trap(self, ctx, member: discord.Member = None, size: str = "15x15"):
        member = member or ctx.author
        if member == ctx.guild.me:
            return
        guild = ctx.guild
        if not self._size_re.fullmatch(size):
            return
        lab_width, lab_height = map(int, size.split("x"))
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
            previous_member_roles = await trap(member, lab.channels)
            lab.previous_member_roles = previous_member_roles
            await lab.update_channels()
            self.channel_to_lab.update({i: lab for i in lab.channels})
            dbmanager.push_lab_to_db(lab)
        await ctx.send("{0.display_name} has been thrown into labyrinth >:)".format(member))
        logger.info("trapped {0.name} from guild {1.id} into labyrinth".format(member, guild))

    @commands.command()
    @commands.check(is_role_powered)
    async def pardon(self, ctx, *, member: discord.Member):
        await self._pardon(member)
        logger.info("pardoned {0.name} from guild {1.id}".format(member, member.guild))

    async def _pardon(self, member: discord.Member):
        folder = find(lambda a: a.name == f"{str(member)}'s labyrinth", member.guild.categories)
        some_channel = next(iter(folder.channels))
        if some_channel in self.channel_to_lab:
            lab = self.channel_to_lab[some_channel]
            await untrap(member, lab.previous_member_roles, folder.channels)
        else:
            await untrap(member, dict(), folder.channels)
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
        if before not in self.channel_to_lab and after not in self.channel_to_lab:
            return
        if after is None:
            return
        if before in self.channel_to_lab:
            lab = self.channel_to_lab[before]
        else:
            lab = self.channel_to_lab[after]
        if after not in self.channel_to_lab:
            await self._pardon(member)
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
            "lab for {0.name} from guild {1.id}: {2} -> {3}".format(member, member.guild, pos_before, pos_after))
        if lab.lab.is_win():
            await self._pardon(member)
        else:
            await member.move_to(lab.center)
            await lab.update_channels()
            dbmanager.update_lab_data_in_db(lab)


def setup(bot):
    bot.add_cog(TrappedCog(bot))
