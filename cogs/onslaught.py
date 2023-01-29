'''
TODO:
- itemprio (alias it wth iprio, item, ip)
  -- build out an embed for the prio
  -- in this embed, show them column wise (row wise for equal prios)
  -- connect up with the wowhead bot? [ITEM] might show? two embeds?
- playerprio (alias it with pprio, player, pp)
  -- stll in dev: get list of prios by the entered playername
- bossloot (alias it with boss, bl)
  -- get boss loot lists?
'''

# Discord util
import discord
from discord.ext import commands
import asyncio #, nest_asyncio

# System util
import os
import sys
from pathlib import *
import string

import warnings
warnings.filterwarnings("ignore")

# Data processing
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials

DATA_PATH = Path.cwd().joinpath("data")

class OnslaughtCog(commands.Cog, name='Onslaught'):
    def __init__(self, bot):
        self.bot = bot
    
    # for debug purposes
    def csv(self, df, filename):
        df.to_csv(DATA_PATH.joinpath(f"{filename}.csv"))
    
    def read_data(self):
        # path to /data. cwd should hopefully let it be cross platform? need to test
        # filename: get specific file name for now
        use_api = False
        if use_api:
            pass
        else:
            # an attempt to avoid hidden files...
            DATA_FILES = [x for x in os.listdir(DATA_PATH) if x[0].isdigit()]
            
            # get data from the most recent prio file
            if len(DATA_FILES) > 0:
                latest_file = sorted(DATA_FILES, reverse=True)[0]
                df = pd.read_excel(DATA_PATH.joinpath(latest_file))
                print(f">> read_data: {latest_file} identified as latest data file. Extracted data.")

                # Drop up to row n since the first rows are ugly and unneccessary
                n = 6
                df = df.copy().iloc[n:]

                num_cols = df.shape[1] # how many columns in our data?

                # clean the columns up
                new_col_names = [
                    'blank1',
                    'blank2',
                    'loot_type',
                    'item',
                    'blank3'
                ]

                # build out the remaining column names for each player
                numbers = [f"player_{num}" for num in list(np.arange(1, num_cols + 1 - len(new_col_names)))]

                # reassign column names
                df.columns = new_col_names + numbers
                return df

    @commands.command(help="$itemprio <item name>: Gets list of priorities on that item.")
    async def itemprio(self, ctx, *, item_name=None):
        # get onslaught data from dir we setup before hand... replaced with Google sheets API eventually
        df = self.read_data()

        # Define the embed for the msg
        embed = discord.Embed(
                #title = "itemprio",
                color = 0x808080,
                timestamp = ctx.message.created_at
            )

        if item_name is not None:
            # Get a list of relevent items
            item_list = list(df['item'].unique())
            item_list = [str(x).lower() for x in item_list]

            if item_name.lower() in item_list:
                df_item = df[df['item'].str.lower() == item_name.lower()]

                # drop irrelev columns
                drop_cols = ['blank1', 'blank2', 'loot_type', 'blank3']
                df_item.drop(columns=drop_cols, inplace=True)
                
                # figure out which columns of player_<> has non-blank values
                player_list = []
                for col in df_item.columns:
                    if 'player' in col:
                        player = str(df_item[col].tolist()[0])
                        if not player.isalpha():
                            player_list.append(player)
                
                player_list_string = ", ".join(player_list)

                # build a ranking dict
                rank_dict = {}
                for player_with_prio in player_list:
                    player = player_with_prio.split(":")[0]
                    rank = float(player_with_prio.split(":")[1].strip())

                    if player not in list(rank_dict.keys()):
                        rank_dict[player] = rank
                    
                df_rank = pd.DataFrame.from_dict(
                    rank_dict.items(),
                )
                df_rank.columns = ['player', 'rank']

                # not needed but ensures proper rank is available
                df_rank.sort_values(by='rank', inplace=True, ascending=False)
                print(df_rank)
                
                await ctx.send(f'Raider prio on {item_name.upper()} >> {rank_dict}')

            else:
                await ctx.send(f"How can I check the item prio if you don't enter a valid item? reeeeeee")
        else:
            await ctx.send(f"How can I check the item prio if you don't enter an item? reeeeeee")
        
    @commands.command(help="$playerprio: Gets & ranks players priorities (basically recreate your sheet).")
    async def playerprio(self, ctx, player_name):
        await ctx.send(f'(in dev) Onslaught priorities for player {player_name}')
        

async def setup(bot):
    await bot.add_cog(OnslaughtCog(bot))
    print("ONSLAUGHT cog loaded.")