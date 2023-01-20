'''
Name: RelsieBot
Author: Relsie, <Mongrels>
Date: January 2023
Purpose: Fun, memes, and usefulness.

TODO: 
>>https://www.quora.com/How-can-I-store-user-input-using-my-discord-py-bot
>>Implement data analysis visualizations and tools for:
   - Mongrels loot data
   - Warcraft logging data 
'''

# Discord imports
import discord
from discord.ext import commands

# Handling listeners
import asyncio

# Utility & data management
from dotenv import load_dotenv, find_dotenv
from io import BytesIO
import datetime, os, sys, pytz, random, pandas as pd

# Acquire proper bot token
load_dotenv(find_dotenv)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

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

# Run the bot
bot.run(BOT_TOKEN)