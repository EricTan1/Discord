# imports
import discord
import asyncio
import json
import sys
import os
import aiohttp

# adding the paths of the different modules in the different folders
# sys.path.append('./GambleGames/')


# create new discord bot obj
client = discord.Client()

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
# await client.send_message(message.channel, 'Say hello')
# waiting for person to respond
# msg = await client.wait_for_message(author=message.author, content='hello')
async def on_message(message):
    ''' (Str) -> None
    This function controls the bot's to ability to respond to
    different commands
    '''
    global _head
    global _messageInitializer
    global _key_dict
    global client
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    else:
        # check if the proper msg intializer is used
        if(message.content.startswith(_messageInitializer)):
            await client.send_message(message.channel, 'Say hello')
        
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


# Run the bot
client.run(TOKEN)
