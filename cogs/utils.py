import discord
from discord.ext import commands
import asyncio #, nest_asyncio
import os

class UtilsCog(commands.Cog, name='Utils'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'I am here, {ctx.message.author.mention}!')

    @commands.command(help="Reloads all or a specified cog")
    async def reload(self, ctx, cog=None):
        print(">> reload command called, reloading neccessary packages")
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
    print("UTILS cog loaded.")