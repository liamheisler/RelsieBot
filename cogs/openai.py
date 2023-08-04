import discord
from discord.ext import commands
import asyncio #, nest_asyncio

import logging
logger = logging.getLogger(__name__)

class OpenAICog(commands.Cog, name='OpenAI'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def helloworld(self, ctx):
        logger.info(f"{ctx.message.author} called $helloworld in channel {ctx.message.channel}")
        await ctx.send(f'Placeholder for Open AI API cog')

async def setup(bot):
    await bot.add_cog(OpenAICog(bot))
    logger.info(f"openai.py cog loaded")