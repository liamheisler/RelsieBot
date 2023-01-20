# Discord/bot imports
from sqlite3 import connect
import discord
from discord.ext import commands
import asyncio

# Local imports
from api_connector import ApiConnector

# Data processing & utils
import pandas as pd
import os
from datetime import datetime, timezone, timedelta

class WarcraftLogsCog(commands.Cog, name='WarcraftLogs'):
    def __init__(self, bot):
        self.bot = bot
    
    def init(self, connector):
        self.wcl = connector # initialize the api connector for WCL
    
    @commands.command(help="$report <rep ID>: Get a report summary for a specific report")
    async def report(self, ctx, rep_ID=None):
        async with ctx.typing():
            if rep_ID is not None:
                await ctx.send(f'Get the logs for {rep_ID}!')
            else:
                await ctx.send(f'Character name not specified! Getting Mongrels logs...')

async def setup(bot):
    await bot.add_cog(WarcraftLogsCog(bot))
    print("WARCRAFT LOGS cog loaded.")