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
