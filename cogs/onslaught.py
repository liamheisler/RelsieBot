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
from rapidfuzz import fuzz

import logging
logger = logging.getLogger(__name__)

import warnings
warnings.filterwarnings("ignore")

# Data processing
import pandas as pd
import numpy as np

# local imports
from utility.database import RelsieDB

DATA_PATH = Path.cwd().joinpath("data")

class OnslaughtCog(commands.Cog, name='Onslaught'):
    def __init__(self, bot):
        self.bot = bot
        self.db = RelsieDB()
        self.active_tier = 'togc'

        self.pp_enabled = False # enables the player prio command
        self.ip_enabled = True  # enables the item prio command
        self.ls_enabled = True  # enables the loot sheet command 
        self.up_enabled = True  # enables the upnext command
    

    # for debug purposes
    def csv(self, df, filename):
        df.to_csv(DATA_PATH.joinpath(f"{filename}.csv"))

    
    def has_numbers(self, inputString):
        return any(char.isdigit() for char in inputString)
    
    
    def read_archived_loot_data(self, tier, item):
        return self.db.get_drops(tier, item)
    
    
    def read_onslaught_data(self, tier = None, item = None):
        return self.db.get_prio(tier, item)
    

    def find_item_name(self, df, tier = None, item_name = None):
        #df = self.db.get_prio(tier)

        item_list = list(df['item'].unique())
        item_list = [str(x).lower() for x in item_list]

        # highest matching similarity score from fuzzss
        scores = {item:fuzz.ratio(item, item_name.lower()) for item in item_list}

        item_name = max(scores, key=scores.get)
        if item_name.lower() in item_list:
            return item_name, True
        else:
            return "", False


    @commands.command(
        help="List priorities for a given item",
        aliases=['ipri', 'ip', 'item']
    )
    async def itemprio(self, ctx, *args):
        if self.ip_enabled:

            # get onslaught data from dir we setup before hand... replaced with Google sheets API eventually
            logger.info(f"{ctx.message.author} called $itemprio in channel {ctx.message.channel}")

            available_tiers = ['ulduar', 'togc', 'icc']
            tier = [arg for arg in args if arg in available_tiers]
            item_name = " ".join([arg for arg in args if arg not in available_tiers])

            if len(tier) == 1:
                tier = tier[0]
            else:
                tier = self.active_tier
            
            logger.info(f"item_name as entered = {item_name}, tier = {tier}")

            df = self.read_onslaught_data(tier, None)

            bot_commands_channel_ID = discord.utils.get(ctx.guild.channels, name="bot-commands").id

            if ctx.message.channel.id == bot_commands_channel_ID:
                if item_name is not None:
                    # Get a list of relevent items
                    #item_name = item_name + "(Heroic)" # just assume it's all heroic

                    item_name, item_found_flag = self.find_item_name(df, tier, item_name)

                    if item_found_flag:
                        async with ctx.typing():
                            # Define the embed for the msg
                            embed = discord.Embed(
                                    title = f"Item priority: {item_name.upper()}",
                                    color = 0x808080,
                                    timestamp = ctx.message.created_at
                                )
                            df_item = df[df['item'].str.lower() == item_name.lower()]
                            
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
                            logger.info(f"itemprio: sent item prio to {ctx.message.author} in channel {ctx.message.channel.id}")

                    else:
                        await ctx.send(f"How can I check the item prio if you don't enter a valid item? reeeeeee")
                else:
                    await ctx.send(f"How can I check the item prio if you don't enter an item? reeeeeee")
            else:
                await ctx.send(f"Sorry, {ctx.message.author.mention}, papa Slinky said no posting loot sheet info outside of bot-commands. Nice try!")
        else:
            await ctx.send(f"Sorry, {ctx.message.author.mention}, that command is disabled at the moment.")
            
        
    @commands.command(
        help="List priorities & competition for given player",
        aliases=['ppri', 'pp', 'player']
    )
    async def playerprio(self, ctx, *args):
        if self.pp_enabled:
            logger.info(f"{ctx.message.author} called $playerprio in channel {ctx.message.channel}")

            available_tiers = ['ulduar', 'togc', 'icc']
            tier = [arg for arg in args if arg in available_tiers]
            player_name = " ".join([arg for arg in args if arg not in available_tiers])

            if len(tier) == 1:
                tier = tier[0]
            else:
                tier = self.active_tier

            logger.info(f"player_name as entered = {player_name}, tier = {tier}")

            df = self.read_onslaught_data(tier, None)

            bot_commands_channel_ID = discord.utils.get(ctx.guild.channels, name="bot-commands").id


            if ctx.message.channel.id == bot_commands_channel_ID:
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
                                player_list = [player for player in list(row) if isinstance(player, str) and ":" in player]
                                
                                player_rank = [float(player.split(":")[1].strip()) for player in player_list if player_name.lower() in player.lower()][0]

                                temp.loc[index] = [row['item'], player_rank, ", ".join(player_list)]

                                df_items = pd.concat([df_items, temp], ignore_index=True)

                            df_items.sort_values(by='max_prio', inplace=True, ascending=False)

                            n = 1
                            for index, row in df_items.iterrows():
                                prio = float(row['max_prio'])
                                item = row['item']
                                competition = row['player_list']

                                embed.add_field(
                                    name = f'Prio: {prio} ~ {item}',
                                    value = f'Competition: {competition}',
                                    inline = False
                                )
                                n += 1

                            await ctx.send(embed=embed)
                            logger.info(f"playerprio: sent playerprio to {ctx.message.author} in channel {ctx.message.channel}")
                    else:
                        await ctx.send(f"Can't get {player_name}'s player prio if they aren't on the sheet!")
                else:
                    await ctx.send(f"Homie I can't get player prios for someone if you don't enter their name!")
            else:
                await ctx.send(f"Sorry, {ctx.message.author.mention}, papa Slinky said no posting player prio info outside of bot-commands. Nice try!")
        else:
            await ctx.send(f"Sorry, {ctx.message.author.mention}, that command is disabled at the moment.")


    @commands.command(
        help="Get the loot sheet for a specific player",
        aliases=['sheet', 'loot', 'ls']
    )
    async def lootsheet(self, ctx, *args):
        if self.ls_enabled:
            logger.info(f"{ctx.message.author} called $lootsheet in channel {ctx.message.channel}")

            available_tiers = ['ulduar', 'togc', 'icc']
            tier = [arg for arg in args if arg in available_tiers]
            player_name = " ".join([arg for arg in args if arg not in available_tiers])

            if len(tier) == 1:
                tier = tier[0]
            else:
                tier = self.active_tier

            logger.info(f"player_name as entered = {player_name}, tier = {tier}")
            
            df = self.read_onslaught_data(tier, None)

            bot_commands_channel_ID = discord.utils.get(ctx.guild.channels, name="bot-commands").id

            if ctx.message.channel.id == bot_commands_channel_ID:
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
                                player_list = [player for player in list(row) if isinstance(player, str) and ":" in player]
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
                            logger.info(f"lootsheet: sent loot sheet to {ctx.message.author} in channel {ctx.message.channel}")
                            #await ctx.send(f"{df_display}")
                    else:
                        await ctx.send(f"Can't get {player_name}'s loot sheet if they aren't on the loot sheet!")
                else:
                    await ctx.send(f"Homie I can't get a loot sheet for someone if you don't enter their name!")
            else:
                await ctx.send(f"Sorry, {ctx.message.author.mention}, papa Slinky said no posting loot sheet info outside of bot-commands. Nice try!")
        else:
            await ctx.send(f"Sorry, {ctx.message.author.mention}, that command is disabled at the moment.")

    
    @commands.command(
        help="Get a list of items that the player is next on",
        aliases=['next', 'un']
    )
    async def upnext(self, ctx, player_name=None):
        if self.up_enabled:
            if player_name is not None:
                await ctx.send(f"Can't get up next items for {player_name} yet :(...")
            else:
                await ctx.send(f"Can't get {player_name}'s items if they aren't on the loot sheet!")
        else:
            await ctx.send(f"Sorry, {ctx.message.author.mention}, that command is disabled at the moment.")


    @commands.command(
        help="Loot / drop history for a specified item",
        aliases=['cd', 'drops', 'dropstats']
    )
    async def checkdrops(self, ctx, *args):
        if self.cd_enabled:
            # get onslaught data from dir we setup before hand... replaced with Google sheets API eventually
            logger.info(f"{ctx.message.author} called $checkdrops in channel {ctx.message.channel}")

            available_tiers = ['ulduar', 'togc', 'icc']
            tier = [arg for arg in args if arg in available_tiers]
            item_name = " ".join([arg for arg in args if arg not in available_tiers])

            if len(tier) == 1:
                tier = tier[0]
            else:
                tier = 'active_tier'
            
            logger.info(f"item_name = {item_name}, tier = {tier}")

            df_arch = self.read_archived_loot_data()
            df = self.read_onslaught_data(tier)

            bot_commands_channel_ID = discord.utils.get(ctx.guild.channels, name="bot-commands").id

            if ctx.message.channel.id == bot_commands_channel_ID:
                if item_name is not None:
                    # Get a list of relevent items
                    #item_name = item_name + "(Heroic)" # just assume it's all heroic

                    dropped_item_list = list(df_arch['Notes'].unique())
                    item_list = list(df['item'].unique())

                    dropped_item_list = [str(x).lower() for x in dropped_item_list]
                    item_list = [str(x).lower() for x in item_list]

                    # highest matching similarity score from fuzzss
                    scores = {item:fuzz.ratio(item, item_name.lower()) for item in item_list}

                    item_name = max(scores, key=scores.get)

                    if item_name.lower() in dropped_item_list:
                        async with ctx.typing():
                            # Define the embed for the msg
                            embed = discord.Embed(
                                    title = f"Drop Stats for: {item_name.upper()}",
                                    color = 0x808080,
                                    timestamp = ctx.message.created_at
                                )
                            
                            loot_history = df_arch[df_arch['Notes'].str.lower() == item_name.lower()]
                            num_drops = loot_history.shape[0]

                            embed.add_field(
                                name = f'Total # of drops:',
                                value = num_drops
                            )

                            for index, row in loot_history.iterrows():
                                passers = [row['Pass 1'], row['Pass 2'], row['Pass 3']]
                                passers = [passer for passer in passers if pd.notnull(passer)]

                                embed.add_field(
                                    name = f"{row['Received']}",
                                    value = f"{row['Date']}",
                                    inline = False
                                )
                                
                            # send msg back to user with the generated embed
                            await ctx.send(embed=embed)
                            logger.info(f"checkdrops: sent drop stats to {ctx.message.author} in channel {ctx.message.channel.id}")

                    else:
                        embed = discord.Embed(
                                title = f"Drop Stats for: {item_name.upper()}",
                                color = 0x808080,
                                timestamp = ctx.message.created_at
                            )
                        embed.add_field(
                            name = f"This item has not dropped yet...yikes.",
                            value = f"$itemprio {item_name}",
                            inline = False
                        )
                        await ctx.send(embed=embed)
                        #await ctx.send(f"$itemprio {item_name}")
                else:
                    await ctx.send(f"How can I check the drop stats if you don't enter an item? reeeeeee")
            else:
                await ctx.send(f"Sorry, {ctx.message.author.mention}, papa Slinky said no posting drop stats info outside of bot-commands. Nice try!")
        else:
            await ctx.send(f"Sorry, {ctx.message.author.mention}, that command is disabled at the moment.")
            

async def setup(bot):
    await bot.add_cog(OnslaughtCog(bot))

    logger.info(f"onslaught.py cog loaded")