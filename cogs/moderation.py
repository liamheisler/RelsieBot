import discord
from discord.ext import commands
import asyncio #, nest_asyncio

class ModerationCog(commands.Cog, name='Moderation'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def purge(self, ctx, number:int=None):
        enabled = False
        if enabled:
            print(">>>purge command called")
            if ctx.message.author.guild_permissions.manage_messages:
                try:
                    if number is None:
                        await ctx.send('You must input a number')
                    else:
                        await ctx.message.delete()
                        
                        deleted = await ctx.message.channel.purge(limit=number)
                        await ctx.send(f'Messages purged by {ctx.message.author.mention}: {len(deleted)}')
                except:
                    await ctx.send("I can't purge messages here, sorry.")
            else:
                await ctx.send("You do not have permissions to use this command!")
        else:
            await ctx.send("Command is disabled, have a chit chat with Relsie if you want this mf thang")

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
    print("MODERATION cog loaded.")