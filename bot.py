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
from pathlib import Path

# setup and config logging
import logging, logging.config, yaml

ROOT = Path(__file__).absolute().parent
CONFIG_FILE = ROOT / 'config' / 'logger.yml'

with open(CONFIG_FILE) as f:
   logging_config = yaml.safe_load(f.read())
   logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)
logger.debug("This is a debug msg")


# Acquire proper bot token and API keys
load_dotenv(find_dotenv())
BOT_TOKEN = os.environ.get("BOT_TOKEN")

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="$", case_insensitive=True, intents=intents)

@bot.event
async def on_ready():
   logger.info(f"Logged in as {bot.user}")
   return await bot.change_presence(activity=discord.Game(name="World of Warcraft Classic {$help}"))

async def load():
   for filename in os.listdir('./cogs'):
      if filename.endswith('.py'):
         await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
   await load()
   await bot.start(BOT_TOKEN)

asyncio.run(main())