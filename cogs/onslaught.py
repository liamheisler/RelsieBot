import discord
from discord.ext import commands
import asyncio #, nest_asyncio

# Data processing
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class OnslaughtCog(commands.Cog, name='Onslaught'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="$itemprio <item name>: Gets list of priorities on that item.")
    async def itemprio(self, ctx, item_name):
        await ctx.send(f'Get the prio for {item_name}!')
        

async def setup(bot):
    await bot.add_cog(OnslaughtCog(bot))
    print("ONSLAUGHT cog loaded.")