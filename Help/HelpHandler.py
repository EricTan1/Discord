# imports
import discord
import asyncio
import json
import sys
import os
import aiohttp
from discord.ext import commands

class HelpHandler(commands.Cog):
    '''
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['h', 'man', 'manual'])
    async def help(self, ctx, *command):
        command = ' '.join(command)
        # if there is specific command to help then

    @commands.command(aliases=['getstarted', 'gstart'])
    async def tutorial(self, ctx):
        # post a indepth summary of the bot with example commands
        pass

    
    @commands.command(aliases=['clist', 'commands'])
    async def commandlist(self, ctx):
        # dms user the command list
        await ctx.author.send(embed=temp_embed, delete_after=20)


