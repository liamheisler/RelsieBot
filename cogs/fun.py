import discord
from discord.ext import commands
import asyncio, nest_asyncio

import random

class FunCog(commands.Cog, name='Fun'):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help="$roll <low> <high>")
    async def roll(self, ctx, low=None, high=None):
        print(">>>roll called")
        if low is None and high is None:
            low = 1; high = 100
        x = str(random.randrange(int(low), int(high)))
        
        rply = f'{ctx.author.mention} rolls {x} ({low}-{high}).'
        await ctx.send(rply)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(FunCog(bot))
    print('FUN cog loaded.')
    
    

