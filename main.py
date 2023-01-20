'''
Name: RelsieBot
Author: Relsie, <Imperium>
Date: April 2021
Purpose: Built for <Imperium> on Wow Clasasic, Westfall NA discord server for fun, memes, and usefulness.

TODO: 
>>https://www.quora.com/How-can-I-store-user-input-using-my-discord-py-bot
>>Implement data analysis visualizations and tools for:
   - Imperium loot data
   - Warcraft logging data 
   - Chilihop's addon thingy? How does that work? 
'''

import discord
from discord.ext import commands
import asyncio, nest_asyncio

from io import BytesIO
import datetime, os, sys, pytz, random, pandas as pd

bot = commands.Bot(command_prefix="$", case_insensitive=True)

@bot.event
async def on_ready():
   print('Loogged in as {0.user}!'.format(bot))
   return await bot.change_presence(activity=discord.Game(name="World of Warcraft Classic {$help}"))

initial_extensions = ['cogs.fun','cogs.moderation'] # Add future cogs
if __name__ == "__main__":
   for extension in initial_extensions:
      try:
         bot.load_extension(extension)
      except Exception as e:
         print(f'Failed to load extention {extension}, error msg: {str(e)}')

bot.run("ODMzMTAxMzgxNjYwNTczNzE2.YHtcHw.rb2r0287XQcUyvAtezpIqWrQuYM")