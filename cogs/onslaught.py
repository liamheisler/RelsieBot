import discord
from discord.ext import commands
import asyncio #, nest_asyncio
import pandas as pd

class OnslaughtCog(commands.Cog, name='Onslaught'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'I am here, {ctx.message.author.mention}!')

    @commands.command()
    async def item_prio(self, ctx, item_name):
        url_prio = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vScKkOmeZnsjBm-hVNDbhuDoPF_Ta2LtQPY_wkEk6DfWPp75AesKjmR97Fqa9rX7w9mhUMTqV_2Ru0J/pubhtml?gid=217967088&single=true'
        df_prio = pd.read_csv(url_prio)
        await ctx.send(f'Prio for {item_name}: {", ".join(df_prio.columns)}!')
        

async def setup(bot):
    await bot.add_cog(OnslaughtCog(bot))
    print("ONSLAUGHT cog loaded.")