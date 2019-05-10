import logging

import discord
from discord.ext import commands

from banlabyrinth import dbmanager

logger = logging.getLogger("banlab")


class DatabaseCleanerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        logger.info("starting removing guild {0.id}".format(guild))
        dbmanager.delete_labs_of_guild(guild.id, list(map(lambda a: a.id, guild.voice_channels)))
        logger.info("removed entities of guild {0.id}".format(guild))


def setup(bot):
    bot.add_cog(DatabaseCleanerCog(bot))
