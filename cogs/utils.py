import discord
from discord.ext import commands
import asyncio #, nest_asyncio
import os

from utility.database import RelsieDB

import logging
logger = logging.getLogger(__name__)

class UtilsCog(commands.Cog, name='Utils'):
    def __init__(self, bot):
        self.bot = bot
        self.db = RelsieDB()


    @commands.command()
    async def ping(self, ctx):
        logger.info(f"{ctx.message.author} called $ping in channel {ctx.message.channel}")
        await ctx.send(f'I am here, {ctx.message.author.mention}!')
        
    
    @commands.command()
    async def refreshdb(self, ctx):
        if ctx.message.author.id == 196824685185466378:
            logger.info("Relsie called DB refresh")
            await ctx.send(f'Request recieved {ctx.message.author.mention}. Refreshing DBs...')

            arch_loot_flag = self.db.update_archived_loot()
            prio_flag = self.db.update_prio()

            if arch_loot_flag and prio_flag:
                await ctx.send(f'Refreshed SQLite3 DBs, {ctx.message.author.mention}!')
            else:
                await ctx.send(f'Could not refresh all DBs, {ctx.message.author.mention}! Archive: {arch_loot_flag} | Prio: {prio_flag}')
        else:
            print("relsbad")
            await ctx.send(f'Sorry, {ctx.message.author.mention}, only Relsie can do this!')


    @commands.command(help="Reloads all or a specified cog")
    async def reload(self, ctx, cog=None):
        logger.info(f"{ctx.message.author} called $reload in channel {ctx.message.channel}")
        if not cog:
            embed = discord.Embed(
                title = "Reloading all cogs!",
                color = 0x808080,
                timestamp = ctx.message.created_at
            )
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await self.bot.unload_extension(f'cogs.{filename[:-3]}')
                    await self.bot.load_extension(f'cogs.{filename[:-3]}')
                    embed.add_field(
                        name = f'Reloaded {filename}',
                        value = '\uFEFF',
                        inline = False
                    )
            await ctx.send(embed=embed)
        else:
            # Need to resolve async here
            embed = discord.Embed(
                title = f"Reloading desired cog: {cog}!",
                color = 0x808080,
                timestamp = ctx.message.created_at
            )
            filename = f"{cog.lower()}.py"
            if not os.path.exists(f"./cogs/{filename}"):
                # if the file does not exist
                embed.add_field(
                    name = f'Failed to reload: {filename}',
                    value = 'Cog does not exist!'

                )
            elif filename.endswith('.py'):
                await self.bot.unload_extension(f'cogs.{filename[:-3]}')
                await self.bot.load_extension(f'cogs.{filename[:-3]}')
                embed.add_field(
                    name = f'Reloaded {filename}',
                    value = '\uFEFF',
                    inline = False
                )   
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UtilsCog(bot))
    logger.info(f"utils.py cog loaded")