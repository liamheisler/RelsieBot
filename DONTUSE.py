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

import discord, asyncio, nest_asyncio
from discord.ext import commands

import datetime, os, pytz, random, pandas as pd
import requests, io, pandas as pd
from io import BytesIO

from sqlalchemy import *
import sqlite3


bot_orig = discord.client()
nest_asyncio.apply()

# Path for the DB only works locally, will have to update to server path
engine = create_engine('sqlite:///Z:\\guild\\RelsieBot\\Database\\relsie.db', echo=True)
cnxn = engine.connect()

fun_df = pd.DataFrame()


# -----------USEFUL FUNCTIONS-----------

def update_atiesh_builder(builder):
    fun_df['Atiesh_Builder'] = builder
  
def update_splinter_count(new_count:int) -> int:
    if new_count >= 40:
      fun_df['Splinter_Count'] = 40
    else:
      fun_df['Splinter_Count'] = int(new_count)

def loot_by_player(data, player=None, instance=None):
    if instance is None:
        instance = 'Naxxramas'
    else:
        instance = instance 
        
    data["player"] = data.player.str.replace("-Westfall","")
    data["instance"] = data.instance.str.replace("-40 Player","")
    
    data = data[data['instance']==instance] 
    
    print("Analyzing loot for player " + player)
    if player is None:
      print("No player specified")
      return pd.DataFrame # return a null DataFrame
    else: # else, return filtered DB
      player_data = data[data["player"].str.lower() == player.lower()]
      player_data = player_data[["player", "date", "gear1", "response"]]
      return player_data
    
def loot_by_class(data, class_in): 
    print("Analyzing loot for class " + class_in)

def loot_by_item(data, item):
    print("Analyzing loot for item " + item)

def loot_by_date(data, date): 
    print("Analyzing loot for date " + date)

def loot_by_type(data, item_type):
    print("Analyzing loot for item type " + item_type)

# -----------MISC/FUN COMMANDS-----------

bot = commands.Bot(command_prefix="$")

# Roll command - currently only rolling 1-100...
@bot.command(help="$roll <low> <high>")
async def roll(ctx, low=None, high=None):
    print(">>>roll called")
    if low is None and high is None:
      low = 1; high = 100
    x = str(random.randrange(int(low), int(high)))
    rply = f'{ctx.author.mention} rolls {x} ({low}-{high}).'
    await ctx.send(rply)
    await ctx.message.delete()

# -----------SPLINTER COMMANDS-----------

@bot.command(help="Updating the current Atiesh Builder")
async def update_builder(ctx, builder=None):
    print(">>>update_builder called")
    if builder is None:
        rply = f"Please provide a name in your command, $update_atiesh_builder <name>"
        await ctx.author.send(rply); return
    else:
        update_atiesh_builder(builder)
        await ctx.author.send(f"{fun_df['Atiesh_Builder'].values[0]} is now building Atiesh!")
    await ctx.message.delete()

@bot.command(help="Updating the current Atiesh Builder's splinter count!")
async def update_splinters(ctx, count:int) -> int:
    print(">>>update_splinters called")
    current_builder = fun_df['Atiesh_Builder'].values[0]
    if count is None:
        rply = f"Please provide a number, $update_splinter_count <current_count>."
        await ctx.author.send(rply); return    
    else:
      if int(count) >= 40:
          update_splinter_count(count)
          rply = f"{current_builder} has reached the required 40 splinters, time for an AQ40. Congrats!"
      else:
          update_splinter_count(count)
          current_count = fun_df['Splinter_Count'].values[0]
          rply = f"{ctx.author.mention} has updated {current_builder}'s splinter count to {current_count}. View with $splinters!"
    await ctx.send(rply)
    await ctx.message.delete()

@bot.command(help="Viewing the current Atiesh Builder's splinter count!")
async def splinters(ctx):
    print(">>>splinters called")
    current_builder = fun_df['Atiesh_Builder'].values[0]
    current_count = int(fun_df['Splinter_Count'].values[0])
    rply = f"{current_builder} curently has {current_count} splinters, only {40-current_count} to go!"
    await ctx.send(rply)
    await ctx.message.delete()

# -----------LOOT DATA COMMANDS-----------

@bot.command() 
async def upload_loot(ctx): 
    print(">>>upload_loot called")
    df = pd.read_excel(BytesIO(await ctx.message.attachments[0].read()))
    
    row = str(df.shape[0]); col = str(df.shape[1])
    await ctx.send("Got your data, currently has " + row + " rows and " + col + " columns.")

@bot.command()
async def player_loot(ctx, player=None, instance=None): 
    print(">>>player_loot called")
    df = db.get("Loot_Data")
    
    print(db.get("Loot_Data"))
    
    player_data = loot_by_player(df, player, instance)
    print(player_data.head())

# -----------MESSAGE ANALYSIS-----------

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # Bot check
    if message.author == bot.user:
      return

# -----------STANDARD ON-READY-----------

@bot.event
async def on_ready():
    
    await bot.change_presence(activity=discord.Game(name="World of Warcraft Classic {$help}"))
    print('Loogged in as {0.user}!'.format(bot))
    
    timechannel = 833103700926791742
    server_tz = pytz.timezone('US/Eastern')
    format = '%I:%M %p'
    
    while True:
        now = datetime.datetime.now(server_tz)
        await bot.get_channel(timechannel).edit(name=f"{now.strftime(format)} ST, rels")
        await asyncio.sleep(60)

cnxn.close()
#bot.run("ODMzMTAxMzgxNjYwNTczNzE2.YHtcHw.rb2r0287XQcUyvAtezpIqWrQuYM")