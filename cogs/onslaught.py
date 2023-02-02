'''
TODO:
- upnext (alias un, next)
  -- get all the items that your the highest on
- playerprio (alias it with boss, bl)
  -- needs work....
     - competition when you're only one on it
     - clean up the output?
- bossloot (alias with boss, bl)
  -- something people want?
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
    
    def has_numbers(self, inputString):
        return any(char.isdigit() for char in inputString)
    
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

    @commands.command(
        help="List priorities for a given item",
        aliases=['ipri', 'ip', 'item']
    )
    async def itemprio(self, ctx, *, item_name=None):
        # get onslaught data from dir we setup before hand... replaced with Google sheets API eventually
        df = self.read_data()

        test_bot_commands_channel_ID = 1070546828480749608
        #mongrels_bot_commands_channel_ID = 996617541315215475

        if ctx.message.channel.id == test_bot_commands_channel_ID:
            if item_name is not None:
                # Get a list of relevent items
                item_list = list(df['item'].unique())
                item_list = [str(x).lower() for x in item_list]

                if item_name.lower() in item_list:
                    async with ctx.typing():
                        # Define the embed for the msg
                        embed = discord.Embed(
                                title = f"Item priority: {item_name.upper()}",
                                color = 0x808080,
                                timestamp = ctx.message.created_at
                            )
                        df_item = df[df['item'].str.lower() == item_name.lower()]

                        # drop irrelev columns
                        drop_cols = ['blank1', 'blank2', 'loot_type', 'blank3']
                        df_item.drop(columns=drop_cols, inplace=True)
                        
                        # figure out which columns of player_<> has non-blank values
                        player_list = []
                        for col in df_item.columns:
                            if 'player' in col:
                                player = str(df_item[col].tolist()[0])
                                if self.has_numbers(player):
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
                            rank_dict.items()
                        )
                        df_rank.columns = ['player', 'prio']
                        
                        # group the players by their prio & put into a final, displayable embed
                        df_display = df_rank.groupby('prio')['player'].apply(list).reset_index()
                        df_display.columns = ['prio', 'players']
                        df_display.sort_values(by='prio', inplace=True, ascending=False)

                        n = 1
                        for index, row in df_display.iterrows():
                            prio = float(row['prio'])
                            players = ", ".join(row['players'])
                            embed.add_field(
                                name = f'{n} ~ {players}',
                                value = f'Priority: {prio}',
                                inline = False
                            )
                            n += 1
                            
                        # send msg back to user with the generated embed
                        await ctx.send(embed=embed)
                        print(">> itemprio: Sent itemprio readout to command caller")

                else:
                    await ctx.send(f"How can I check the item prio if you don't enter a valid item? reeeeeee")
            else:
                await ctx.send(f"How can I check the item prio if you don't enter an item? reeeeeee")
        else:
            await ctx.send(f"Sorry, {ctx.message.author.mention}, papa Hammerz said no posting loot sheet info outside of bot-commands. Nice try!")
            
        
    @commands.command(
        help="List priorities & competition for given player",
        aliases=['ppri', 'pp', 'player']
    )
    async def playerprio(self, ctx, player_name):
        # start playerprio
        df = self.read_data().fillna("")

        test_bot_commands_channel_ID = 1070546828480749608
        #mongrels_bot_commands_channel_ID = 996617541315215475

        enabled = False

        if enabled:
            if ctx.message.channel.id == test_bot_commands_channel_ID:
                if player_name is not None:            
                    df_player = df[df.apply(lambda r: r.str.contains(player_name, case=False).any(), axis=1)]
                    
                    if not df_player.empty:
                        async with ctx.typing():
                            embed = discord.Embed(
                                title = f"Top 25 Priorities & Competition for: {player_name.upper()}",
                                color = 0x808080,
                                timestamp = ctx.message.created_at
                            )

                            item_dict = {}
                            df_items = pd.DataFrame(columns=["item", "max_prio", "player_list"])

                            for index, row in df_player.iterrows():
                                temp = pd.DataFrame(columns=["item", "max_prio", "player_list"])

                                # list of players for that item
                                player_list = [player for player in list(row) if ":" in player]
                                player_rank = [float(player.split(":")[1].strip()) for player in player_list if player_name.lower() in player.lower()][0]

                                temp.loc[index] = [row['item'], player_rank, ", ".join(player_list)]

                                df_items = pd.concat([df_items, temp], ignore_index=True)

                            df_items.sort_values(by='max_prio', inplace=True, ascending=False)

                            n = 1
                            for index, row in df_items.iterrows():
                                #print(row)
                                prio = float(row['max_prio'])
                                item = row['item']
                                competition = row['player_list']

                                #print(f"{prio} | {item} | {competition}")

                                embed.add_field(
                                    name = f'Prio: {prio} ~ {item}',
                                    value = f'Competition: {competition}',
                                    inline = False
                                )
                                n += 1

                            await ctx.send(embed=embed)
                            print(">> playerprio: Sent player prio readout to command caller")
                    else:
                        await ctx.send(f"Can't get {player_name}'s loot sheet if they aren't on the loot sheet!")
                else:
                    await ctx.send(f"Homie I can't get a loot sheet for someone if you don't enter their name!")
            else:
                await ctx.send(f"Sorry, {ctx.message.author.mention}, papa Hammerz said no posting loot sheet info outside of bot-commands. Nice try!")
        else:
            await ctx.send("That mf Relsie disabled this command, didn't think it was that helpful. To be replaced with a upnext type of command.")


    @commands.command(
        help="Get the loot sheet for that player",
        aliases=['sheet', 'loot', 'ls']
    )
    async def lootsheet(self, ctx, player_name=None):

        df = self.read_data().fillna("")

        test_bot_commands_channel_ID = 1070546828480749608
        #mongrels_bot_commands_channel_ID = 996617541315215475

        if ctx.message.channel.id == test_bot_commands_channel_ID:
            if player_name is not None:            
                df_player = df[df.apply(lambda r: r.str.contains(player_name, case=False).any(), axis=1)]
                
                if not df_player.empty:
                    async with ctx.typing():
                        embed = discord.Embed(
                            title = f"Top 25 items for: {player_name.upper()}",
                            color = 0x808080,
                            timestamp = ctx.message.created_at
                        )

                        item_dict = {}
                        df_items = pd.DataFrame(columns=["item", "max_prio", "player_list"])

                        for index, row in df_player.iterrows():
                            temp = pd.DataFrame(columns=["item", "max_prio", "player_list"])

                            # list of players for that item
                            player_list = [player for player in list(row) if ":" in player]
                            player_rank = [float(player.split(":")[1].strip()) for player in player_list if player_name.lower() in player.lower()][0]

                            temp.loc[index] = [row['item'], player_rank, ", ".join(player_list)]

                            df_items = pd.concat([df_items, temp], ignore_index=True)

                            df_display = df_items.groupby('max_prio')['item'].apply(list).reset_index()

                        df_display.sort_values(by='max_prio', inplace=True, ascending=False)

                        n = 1
                        for index, row in df_display.iterrows():
                            prio = float(row['max_prio'])
                            items = ", ".join(row['item'])
                            embed.add_field(
                                name = f'{items}',
                                value = f'{n} : Priority: {prio}',
                                inline = False
                            )
                            n += 1

                        await ctx.send(embed=embed)
                        print(">> lootsheet: Sent loot sheet to command caller")
                        #await ctx.send(f"{df_display}")
                else:
                    await ctx.send(f"Can't get {player_name}'s loot sheet if they aren't on the loot sheet!")
            else:
                await ctx.send(f"Homie I can't get a loot sheet for someone if you don't enter their name!")
        else:
            await ctx.send(f"Sorry, {ctx.message.author.mention}, papa Hammerz said no posting loot sheet info outside of bot-commands. Nice try!")

    
    @commands.command(
        help="Get a list of items that the player is next on",
        aliases=['next', 'un']
    )
    async def upnext(self, ctx, player_name=None):
        if player_name is not None:
            await ctx.send(f"Can't get up next items for {player_name} yet :(...")
        else:
            await ctx.send(f"Can't get {player_name}'s items if they aren't on the loot sheet!")
        

async def setup(bot):
    await bot.add_cog(OnslaughtCog(bot))
    print("ONSLAUGHT cog loaded.")