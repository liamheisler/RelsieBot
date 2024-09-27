'''
Messing with the Blizzard API
'''
# discord utility
import discord
from discord.ext import commands

# local utility
from utility.database import RelsieDB
from utility.blizzard_api import BlizzardAPI

# logging
import logging
logger = logging.getLogger(__name__)

class BlizzardCog(commands.Cog, name='BlizzardAPI'):

    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(help="")
    async def blizzping(self, ctx):
        await ctx.send("yo")


async def setup(bot):
    await bot.add_cog(BlizzardCog(bot))
    logger.info(f"blizzard.py cog loaded")