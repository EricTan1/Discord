# imports
import discord
import asyncio
import json
import sys
import os
import aiohttp
from discord.ext import commands

# music player
import youtube_dl

# adding the paths of the different modules in the different folders
sys.path.append('./Games/')
sys.path.append('./Music/')
sys.path.append('./API/')

# Games imports
# Music player
from MusicPlayer import MusicPlayer
# AMQ imports
from Amq import Amq
# API imports
from BotApiHandler import BotApiHandler
from LeagueWrapper import LeagueWrapper
from OsuWrapper import OsuWrapper
from AnilistWrapper import AnilistWrapper
# Setting global variables
_command_prefix = '$'
players = {}

# create new discord bot obj
client = commands.Bot(command_prefix=_command_prefix)

# read the information for the api keys and put them in a dictionary
_key_dict = None
KEY_PATH = "Data/keys.json"
bah = None
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
    global _key_dict
    global bah
    # load up data if it exists if not then create new data
    _persona_dict = None
    PERSONA_PATH = "Data/persona.json"
    PERSONABACKUP_PATH = "Data/personabackup.json"
    try:
        with open(PERSONA_PATH, 'r') as data:
            _persona_dict = json.load(data)
        # now save the info as "Backup"
        print("successful load")
    except:
        print("empty/invalid json file for persona keys")
        _persona_dict = dict()
    # setting up api
    league_wrap = LeagueWrapper(_key_dict.get("LEAGUE"))
    osu_wrap = OsuWrapper(_key_dict.get("OSU"))
    anilist_wrap = AnilistWrapper("https://graphql.anilist.co/")
    
    bah = BotApiHandler(client, _persona_dict, league_wrapper=league_wrap,
                        osu_wrapper=osu_wrap, anilist_wrapper=anilist_wrap)
    # adding the new commands
    client.add_cog(bah)
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
        # if the author of the message isn't already in the same voice channel
        # as the bot
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


# global var b/c check function cant share vars with outter function
options = 0


@client.command()
async def game(ctx, game):
    global options
    global bah
    if(game.upper() == "AMQ"):
        channel = ctx.channel
        # get info to start game
        await channel.send('State number of rounds\nDefault: 20', delete_after=40)

        def check(m):
            global options
            check_bool = True
            options = m.content
            # if the parameter they passed in isnt an integer then
            # ignore it until they pass one in
            try:
                options = int(options)
            except Exception:
                check_bool = False
            return check_bool and m.channel == channel

        msg = await client.wait_for('message', check=check)

        await channel.send('Starting Game', delete_after=10)
        participants = ctx.guild.voice_client.channel.members
        anime_list = []
        # loop thur all participants and get the animelist username
        for people in participants:
            await bah.setup_profile(ctx.guild.id, people.id)
            if(await bah.get_animelist(ctx.guild.id, people.id) != None):
                anime_list.append(await bah.get_animelist(ctx.guild.id, people.id))
        if(len(anime_list) == 0):
            await channel.send('No one is logged in to anilist. Please log in to one via login command\nPlaying with Default list\nDefault List: https://anilist.co/user/woahs/', delete_after=40)
            current_game = Amq(client, participants,
                               ctx.message.channel, ctx.guild.voice_client,
                               MusicPlayer(client), rounds=options, time_sec=35.0,
                               anilist_wrapper=AnilistWrapper("https://graphql.anilist.co/"))
        else:
            current_game = Amq(client, participants,
                               ctx.message.channel, ctx.guild.voice_client,
                               MusicPlayer(client), rounds=options, time_sec=35.0,
                               anime_list=anime_list,
                               anilist_wrapper=AnilistWrapper("https://graphql.anilist.co/"))
        client.add_cog(current_game)
        await current_game.set_up()
        await current_game.play_game()
        # remove cog after game finishes




# Run the bot
client.run(TOKEN)
