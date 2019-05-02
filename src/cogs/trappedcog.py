import logging
import re

import discord
from discord.ext import commands
from discord.utils import find

from src.lab import LabyrinthWalker, gen_lab, letters_reversed, ROAD, WALL
from src.utils import trap, untrap, check_role_existence, is_role_powered

logger = logging.getLogger("banlab")
CENTER_ICON = "\u2718"

LEFT_ARROW = "\u21d0"

DOWN_ARROW = "\u21d3"

RIGHT_ARROW = "\u21d2"

UP_ARROW = "\u21d1"

CLOSED_ICON = "\u26d4"


class Labyrinth:
    def __init__(self, lab: LabyrinthWalker, folder: discord.CategoryChannel, up, right, down, left, center):
        self.lab = lab
        self.folder = folder
        self.up = up
        self.right = right
        self.down = down
        self.left = left
        self.center = center
        self.channels = {up, right, center, down, left}
        self.channel_to_direction = {
            self.up: 'N',
            self.right: 'E',
            self.down: 'S',
            self.left: 'W'
        }
        self.direction_to_channel = {
            'N': self.up,
            'E': self.right,
            'S': self.down,
            'W': self.left
        }
        self.channel_to_true_name = {
            self.up: UP_ARROW,
            self.right: RIGHT_ARROW,
            self.down: DOWN_ARROW,
            self.left: LEFT_ARROW
        }

    async def update_channels(self):
        for channel in self.channels:
            if channel == self.center:
                continue
            direction = self.channel_to_direction[channel]
            wall = letters_reversed[direction]
            if self.lab.curr.walls[wall] == ROAD and channel.name != self.channel_to_true_name[channel]:
                await channel.edit(name=self.channel_to_true_name[channel])
            elif self.lab.curr.walls[wall] == WALL and channel.name != CLOSED_ICON:
                await channel.edit(name=CLOSED_ICON)

    def is_wall(self, channel):
        direction = self.channel_to_direction[channel]
        wall = letters_reversed[direction]
        return self.lab.curr.walls[wall] == WALL


class TrappedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._size_re = re.compile(r"^\d{1,2}x\d{1,2}$")
        self.channel_to_lab = dict()
        self.member_to_lab = dict()
        self.role = None

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
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False,
                                                            create_instant_invite=False),
            member: discord.PermissionOverwrite(read_messages=True, connect=True, create_instant_invite=False),
            self.role: discord.PermissionOverwrite(read_messages=True),
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
            lab = Labyrinth(lw, folder, up, right, down, left, center)
            try:
                await member.move_to(center)
            except discord.errors.HTTPException:
                pass
            await trap(member, lab.channels)
            await lab.update_channels()
            self.member_to_lab[member] = lab
            self.channel_to_lab.update({i: lab for i in lab.channels})
        await ctx.send("{0.display_name} has been thrown into labyrinth >:)".format(member))
        logger.info("trapped {0.name} from guild {1.id} into labyrinth".format(member, guild))

    @commands.command()
    @commands.check(is_role_powered)
    async def pardon(self, ctx, *, member: discord.Member):
        await self._pardon(member)
        logger.info("pardoned {0.name} from guild {1.id}".format(member, member.guild))

    async def _pardon(self, member: discord.Member):
        if member not in self.member_to_lab:
            lab = find(lambda a: a.name == f"{str(member)}'s labyrinth", member.guild.categories)
        else:
            lab = self.member_to_lab[member]
        await untrap(member, lab.channels)
        for channel in lab.channels:
            await channel.delete()
            if channel in self.channel_to_lab:
                del self.channel_to_lab[channel]
        await lab.folder.delete()
        if member in self.member_to_lab:
            del self.member_to_lab[member]

    async def bot_check_once(self, ctx):
        self.role = await check_role_existence(ctx)
        return True

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
        move_result = lab.lab.move_into(direction)
        print(lab.lab)
        if lab.lab.is_win():
            await self._pardon(member)
        else:
            await member.move_to(lab.center)
            await lab.update_channels()


def setup(bot):
    bot.add_cog(TrappedCog(bot))
