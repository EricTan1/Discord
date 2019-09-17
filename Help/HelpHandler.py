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
        temp_embed = discord.Embed()
        # if there is specific command to help then
        if (len(command) != 0):
            try:
                path = "Help/" + command.lower() + "H.txt"
                f = open(path, "r")
                contents = f.read()
                temp_embed.color = 16408551
                temp_embed.title = command.lower() + " help"
                temp_embed.description = contents
                await ctx.send(embed=temp_embed)
            except:
                temp_embed.color = 15158332
                temp_embed.title = "Error"
                temp_embed.description = "not a valid search command"
                await ctx.send(embed=temp_embed)
        else:
                temp_embed.color = 16408551
                temp_embed.title = "Help introduction"
                temp_embed.description = "Check out '<command_prefix> commandlist' for list of commands and '<command_prefix>help help' on how to use the help command"
                await ctx.send(embed=temp_embed)


    @commands.command(aliases=['getstarted', 'tut'])
    async def tutorial(self, ctx):
        # post a indepth summary of the bot with example commands
        path = "Help/tutorial.txt"
        f = open(path, "r")
        contents = f.read()        
        temp_embed = discord.Embed()
        temp_embed.color = 16408551
        temp_embed.title = "Tutorial"
        temp_embed.description = contents
        await ctx.send(embed=temp_embed)

    
    @commands.command(aliases=['clist', 'commands'])
    async def commandlist(self, ctx):
        # dms user the command list
        path = "Help/commandlist.txt"
        f = open(path, "r")
        contents = f.read()
        temp_embed = discord.Embed()
        temp_embed.color = 16408551
        temp_embed.title = "Command List"
        temp_embed.description = contents
        await ctx.author.send(embed=temp_embed)


