# imports
import discord
import asyncio
import requests
import json
import sys
import os
import aiohttp
from discord.ext import commands
from queue import Queue
from random import randrange
from Game import Game
from importlib import reload
import aiohttp

class Amq(commands.Cog):
    ''' This class is responsible for the entire anime music quiz game
    
    '''

    def __init__(self, bot, participants, text_channel, voice_channel, music_player, rounds=20, time_sec=35.0, anime_list=['woahs'], anilist_wrapper=None):
        ''' (Amq, discord.Client, List of user, int, double, List of Strings) -> Amq
        Takes in the discord.client obj
        Takes in list of discord.user obj
        Takes in discord.textchannel obj
        Takes in dsicord.voicechannel obj
        Takes in the Musicplaer obj
        '''
        # super().__init__(bot)
        self.bot = bot
        self.rounds = rounds
        self.music_player = music_player
        self.text_channel = text_channel
        self.voice_channel = voice_channel
        self.time_per_song = time_sec
        self.test = None
        self.anime_list = anime_list
        # index 0 = english, index 1 = romaji, index 2 = japanese
        self.stop_words = []
        self.participants = participants
        self.anilist_wrapper = anilist_wrapper


    async def set_up(self):
        ''' (Amq) -> None
        The set up method for Amq. This method loads in the stopwords, creates
        the player objs, fetches and randomizes the animeLists and loads in the
        anime information
        '''
        # Loading stop words
        # english
        self.stop_words.append(await self.load_stopwords("Games/stopwords/english.txt"))
        self.stop_words.append(await self.load_stopwords("Games/stopwords/romaji.txt"))
        self.stop_words.append(await self.load_stopwords("Games/stopwords/japanese.txt"))
        p_list = []
        anime_list = []
        # initializing the player list
        for person in self.participants:
            p_list.append(Player(person.id, person.name, person.mention))
        # loop through all the anime lists and union the two lists w/o repeats
        # All strings here
        for index in range(len(self.anime_list)):
            # Union two sets (no repeats)
            # import AniList
            second_list = []
            # based on user
            response = await self.anilist_wrapper.get_aniList(self.anime_list[index])

            # response = requests.post(url, json={'query': query, 'variables': variables})
            list_data=response.get("data").get("MediaListCollection").get('lists')

            for ani_lists in list_data:
                for anime in ani_lists.get("entries"):
                    second_list.append(anime.get("media").get("title").get("english"))

            in_first=set(anime_list)
            in_second=set(second_list)
            in_second_but_not_in_first=in_second - in_first
            anime_list=anime_list + list(in_second_but_not_in_first)            

        self.participants = p_list
        self.aniList_personal = anime_list
        # RANDO ANIME CHOOSING CODE HERE
        self.animeQueue = Queue(self.rounds)
        rangelimit = self.rounds
        if(len(self.aniList_personal) < self.rounds):
            rangelimit = len(self.aniList_personal)
        for x in range(rangelimit):
                song_name = self.aniList_personal.pop(randrange(len(self.aniList_personal) - 1))
                if(song_name != None):
                    res = await self.anilist_wrapper.get_aniListAnime_single(song_name)
                    anime_data = res.get("data").get("Media")
                    name_types = []
                    name_types.append(anime_data.get('title').get('english'))
                    name_types.append(anime_data.get('title').get('romaji'))
                    name_types.append(anime_data.get('title').get('native'))
                    pic_url = anime_data.get('coverImage').get('medium')
                    site_url = anime_data.get('siteUrl')
                    desc = anime_data.get('description')
                    self.animeQueue.put(Song(anime_data.get('title').get('english'), name_types, pic_url, site_url, desc))

    async def play_game(self):
        ''' (Amq) -> None
        This method starts the entire game. It loops through the randomized anime
        list and plays the songs with the optional skip
        '''
        while (not self.animeQueue.empty()):
            current_song = self.animeQueue.get()
            # play the song

            if(self.text_channel.guild.voice_client != None):
                # if the bot currently has audio on then stop it
                if(self.text_channel.guild.voice_client.is_playing()):
                    self.text_channel.guild.voice_client.stop()
                audio_source = discord.FFmpegPCMAudio(self.music_player.download("test_song", current_song.english_name.replace(':', ' ') + " opening tv size"))
                try:
                    await self.music_player.play_music(audio_source, self.text_channel, self.voice_channel)
                except:
                    await self.text_channel.send("Error in getting URL", delete_after=5)
                    continue
                await self.text_channel.send("Playing Song", delete_after=5)

            channel = self.text_channel

            msg = await channel.send('Send me that \U0001f44e reaction, to skip\nEveryone participating needs to react in order to skip.', delete_after=self.time_per_song)
            await msg.add_reaction('\U0001f44e')

            def check(reaction, user):
                return str(reaction.emoji) == '\U0001f44e' and reaction.count >= len(self.participants)

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=self.time_per_song, check=check)
            except asyncio.TimeoutError:
                await self.text_channel.send("Song is done", delete_after=5)
            else:
                await self.text_channel.send("Song is done", delete_after=5)
                await channel.send('Current Song has been skipped \U0001f44e', delete_after=5)
            # if the bot currently has audio on then stop it
            if(self.text_channel.guild.voice_client.is_playing()):
                await self.music_player.stop_music(self.text_channel)
            await self._calculate_round_results(current_song)
        await self.end_game()


    async def _calculate_round_results(self, current_song):
        ''' (Amq, Song) -> None
        Takes in the current song and calculates/updates the score based on the 
        current song/player's guess. This method removes the stop words from the
        titles in their respective languages and checks based on the exact name or
        the guess based on words that are not stop words in the title
        '''
        # check answers and reward points
        for players in self.participants:
            # only if the players tried to guess
            if(players.guess != None):
                # check each time for english jap and romaji variations
                for index in range(3):
                    if(players.guess.upper() == current_song.name[index].upper()):
                        await self.text_channel.send(players.mention + " guessed it correctly!", delete_after=15)
                        players.score = players.score + 1
                        break
                    else:
                        check_guess = True
                        stop_list = self.stop_words[index]
                        # change the title to a list
                        title_name = current_song.name[index].upper().replace(':', '').split(' ')
                        # remove stop words from title
                        in_first = set(self.stop_words[index])
                        in_second = set(title_name)
                        phrase = in_second - in_first

                        # check if each word is in the list
                        temp_guess=players.guess.split(' ')
                        for words in temp_guess:
                            if(not (words.upper() in phrase)):
                                check_guess=False
                        if(check_guess == True):
                            await self.text_channel.send(players.mention + " guessed it correctly!", delete_after=15)
                            players.score=players.score + 1
                            break

                # reset the guesses
                players.guess=None
        # send answer
        temp_embed=discord.Embed()
        anime_title=""
        for titles in current_song.name:
            anime_title=anime_title + titles + " | "

        temp_embed.title=anime_title
        temp_embed.color=3900661
        temp_embed.url=current_song.website_url
        temp_embed.set_image(url=current_song.picture_url)
        temp_embed.description = current_song.description
        await self.text_channel.send("The correct answer is: ", embed=temp_embed, delete_after=10)
        # send answer
        temp_embed2 = discord.Embed()
        temp_embed2.title = "Anime Music Quiz Results"
        temp_embed2.color = 4652906
        for players in self.participants:
            if(players.id != self.bot.user.id):
                temp_embed.add_field(name=players.name, value="Score: " + str(players.score), inline="false")
        await self.text_channel.send(embed=temp_embed2, delete_after=10)

    async def end_game(self):
        ''' (Amq) -> None
        This method removes the Guess and Search command because the game is
        finished. It also prints an embedded discord message of the endgame 
        scoreboard
        '''
        # disconnect the bot from VC
        guild_list = self.bot.guilds
        for guild in guild_list:
            if(guild.id == self.text_channel.guild.id):
                if(guild.voice_client != None):
                    await guild.voice_client.disconnect()
        # remove the commands
        self.bot.remove_cog("Amq")
        # send answer
        temp_embed = discord.Embed()
        temp_embed.title="Anime Music Quiz Results"
        temp_embed.color=4652906
        for players in self.participants:
            if(players.id != self.bot.user.id):
                temp_embed.add_field(name=players.name, value="Score: " + str(players.score), inline="false")
        await self.text_channel.send(embed=temp_embed)

    @commands.command(aliases=['g'])
    async def guess(self, ctx, *guess):
        ''' (Amq, discord.context, Str) -> None
        Updates the players current guess
        '''
        # combine the guess fragments together and get rid of spoilers
        search = ' '.join(guess).replace('|', '')
        for players in self.participants:
            if(players.id == ctx.message.author.id):
                players.guess = search

    @commands.command(aliases=['s'])
    async def search(self, ctx, *anime):
        ''' (Amq, discord.context, Str) -> None
        DMs the user searching for the anime with results
        of animes that have similar title in order to assist with
        the guesses
        '''
        search = ' '.join(anime).replace('|', '')

        res = await self.anilist_wrapper.get_aniListAnime(search)
        # if there is a response
        if(res != None or res.get("data") != None):
            anime_data = res.get("data").get("Page")
            anime_data = anime_data.get("media")
            temp_embed = discord.Embed()
            temp_embed.title = "Anime Search Results"
            temp_embed.color = 786236
            for anime in anime_data:
                temp_embed.add_field(name=anime.get('title').get('english'), value=anime.get('title').get('romaji'), inline="false")

            await ctx.author.send(embed=temp_embed, delete_after=20)
        else:
            await ctx.author.send("No search results", delete_after=5)

    async def load_stopwords(self, file_name):
        lineList = list()
        # with open(file_name, encoding="utf8") as f:
        lineList = [line.rstrip('\n').upper() for line in open(file_name, encoding="utf8")]
        return lineList

class Player():
    ''' Player class with guess and score attribute for Amq
    '''
    def __init__(self, id, name, mention, guess=None):
        self.score = 0
        self.id = id
        self.name = name
        self.mention = mention
        self.guess = guess


class Song():
    ''' Song class with details such as names,urls and desc
    '''
    def __init__(self, english_name, name: set, picture_url: str, website_url: str, description: str):
        self.name = name
        self.english_name = english_name
        self.picture_url = picture_url
        self.website_url = website_url
        self.description = description
