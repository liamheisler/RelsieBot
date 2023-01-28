import discord
from discord.ext import commands
import asyncio #, nest_asyncio

class OpenAICog(commands.Cog, name='OpenAI'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def helloworld(self, ctx):
        await ctx.send(f'Placeholder for Open AI API cog')

async def setup(bot):
    await bot.add_cog(OpenAICog(bot))
    print("OPEN AI cog loaded.")