# imports
import discord
import asyncio
import json
import sys
import os
import aiohttp
import youtube_dl
from discord.ext import commands
# adding the paths of the different modules in the different folders
# sys.path.append('./GambleGames/')

# Setting global variables
_command_prefix = '$'
players = {}

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

@client.command()
async def goodnight(ctx):
    await client.send_message(ctx.message.channel, "GoodNight!")

@client.command()
async def connect(ctx):
    # get the voice channel of the author and connect to it
    # if there is no voice channel then send an error message
    author_voice = ctx.message.author.voice
    if(author_voice == None):
        temp_embed = discord.Embed()
        temp_embed.color = 15158332
        temp_embed.title = "Error"
        temp_embed.description = "You are not currently in a voice channel"
        await ctx.send(embed=temp_embed)
    # if the bot is already in a voice channel
    elif(ctx.guild.voice_client != None):
        print("already in a voice channel")
        # if the author of the message isn't already in the same voice channel as the bot
        if(ctx.guild.voice_client.channel != author_voice.channel):
            await ctx.guild.voice_client.disconnect()
            await author_voice.channel.connect()
    # connect the bot to a voice channel of the author
    else:
        await author_voice.channel.connect()
        


@client.command()
async def disconnect(ctx):
    # disconnect the bot from the voice if it is connected
    if(ctx.guild.voice_client != None):
        await ctx.guild.voice_client.disconnect()


@client.command()
async def close(ctx):
    # embeded message to show that the bot is shut down
    temp_embed = discord.Embed()
    temp_embed.color = 3066993
    temp_embed.title = "Closed"
    temp_embed.description = "Bot has been successfully closed"
    await ctx.send(embed=temp_embed)
    # shut down the bot
    await client.close()

@client.command()
async def play(ctx, url):
    # if the bot current has audio on then stop it
    if(ctx.guild.voice_client.is_playing()):
        ctx.guild.voice_client.stop()
    audio_source = discord.FFmpegPCMAudio(await download("test_song", url)["audio"])
    ctx.guild.voice_client.play(audio_source)


async def download(title, video_url):
    ydl_opts = {
        'outtmpl': '{}.%(ext)s'.format(title),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return {
        'audio': '{}.mp3'.format(title),
        'title': title,
    }


# Run the bot
client.run(TOKEN)
