# imports
import discord
import asyncio
import json
import sys
import os
import aiohttp
from discord.ext import commands
# adding the paths of the different modules in the different folders
# sys.path.append('./GambleGames/')

# Setting global variables
_command_prefix = '$'

# create new discord bot obj
client = commands.Bot(command_prefix=_command_prefix)



# read the information for the api keys and put them in a dictionary
_key_dict = None
KEY_PATH = "Data/keys.json"
try:
    with open(KEY_PATH, 'r') as data:
        _key_dict = json.load(data)
except:
    print("empty/invalid json file for api keys")
# set the discord API key
TOKEN = _key_dict["DISCORD"]


        
@client.event
async def on_ready():
    ''' () -> None
    This function initializes the bot by setting up the information from
    the database in the local systems and using that information to create
    the linkedlist of persona objects.
    '''
    print("The bot is ready!")

async def set_messageInt(messageInitializer):
    ''' (str)->str
    This function takes in a message init and sets it
    '''
    global _messageInitializer
    _messageInitializer = messageInitializer

@client.command(pass_context=True)
async def goodnight(ctx):
    await client.send_message(ctx.message.channel, "GoodNight!")

# Run the bot
client.run(TOKEN)
