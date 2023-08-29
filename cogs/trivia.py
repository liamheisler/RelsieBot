import discord
from discord.ext import commands
import asyncio #, nest_asyncio
import os
import html
import random
import string

from utility.database import RelsieDB
from utility.database import TriviaDB

import logging
logger = logging.getLogger(__name__)

class TriviaCog(commands.Cog, name='Trivia'):
    def __init__(self, bot):
        self.bot = bot
        self.db = RelsieDB()
        self.trivia_db = TriviaDB()


    @commands.command()
    async def trivia(self, ctx):
        logger.info(f"{ctx.message.author} called $trivia in channel {ctx.message.channel}")

        # Grab a question!
        self.current_question_data = self.trivia_db.get_question()

        self.where_was_question_asked = ctx.message.channel.id

        self.current_category = self.current_question_data['category']
        self.current_question_type = self.current_question_data['type']
        self.current_difficulty = self.current_question_data['difficulty']
        self.current_question = html.unescape(self.current_question_data['question'])
        self.current_correct_ans = html.unescape(self.current_question_data['correct_answer'])
        self.current_incorrect_ans = self.current_question_data['incorrect_answers']

        # build an available answers list:
        available_answers = self.current_incorrect_ans + [self.current_correct_ans]
        random.shuffle(available_answers)

        alphabet_opts = list(string.ascii_uppercase)[0:len(available_answers)]

        available_answers_dict = dict(zip(available_answers, alphabet_opts))
        self.current_available_answers_dict = available_answers_dict

        self.current_correct_alphabet_option = available_answers_dict[self.current_correct_ans]

        async with ctx.typing():
            # Define the embed for the msg
            embed = discord.Embed(
                    title = f"{html.unescape(self.current_question)}",
                    color = 0x808080,
                    timestamp = ctx.message.created_at
            )

            if self.current_question_type == 'boolean':
                embed.add_field(
                    name=f'**{"True or False"}**',
                    value=f'',
                    inline=False
                )
            else:
                for answer, letter in available_answers_dict.items():
                    if self.current_question_type == 'multiple':
                        embed.add_field(
                            name=f'{letter}:\t*{html.unescape(answer)}*',
                            value='',
                            inline=False
                        )
            
            embed.set_footer(
                text=f'< category: {self.current_category} | difficulty: {self.current_difficulty} > '
            )

        logger.info(f"Question asked in {self.where_was_question_asked}. Correct answer: {self.current_correct_alphabet_option}: {self.current_correct_ans}")
        await ctx.send(embed=embed)
    
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # TODO: verify that the message came from the same channel in which the question was asked
        current_correct_answer = self.current_correct_ans
        current_correct_alphabet_opt = self.current_correct_alphabet_option

        available_answers = [ans.lower() for ans in list(self.current_available_answers_dict.keys())]
        available_opts = [ans.lower() for ans in list(self.current_available_answers_dict.values())]


        if message.author == self.bot.user:
            return
        
        if message.channel.id == self.where_was_question_asked:
            msg = message.content.lower()

            if msg.lower() in available_answers or msg.lower() in available_opts:
                if msg.lower() == current_correct_answer.lower() or msg.lower() == current_correct_alphabet_opt.lower():
                    await message.add_reaction(discord.utils.get(self.bot.emojis, name='gdubb'))
                    await message.channel.send(f"{current_correct_answer} is correct. Nice work {message.author.mention}!")
                else:
                    await message.add_reaction(discord.utils.get(self.bot.emojis, name='panik'))


async def setup(bot):
    await bot.add_cog(TriviaCog(bot))
    logger.info(f"trivia.py cog loaded")