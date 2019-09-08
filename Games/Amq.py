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

    def __init__(self, bot, participants, text_channel, voice_channel, music_player, rounds=3, time_sec=20.0):
        ''' (Amq, discord.Client, List of Strings, int, double,) -> Amq
        '''
        # super().__init__(bot)
        self.bot = bot
        self.rounds = rounds
        self.music_player = music_player
        self.text_channel = text_channel
        self.voice_channel = voice_channel
        self.time_per_song = time_sec
        self.test = None
        # index 0 = english, index 1 = romaji, index 2 = japanese
        self.stop_words = []
        self.participants = participants


    async def set_up(self):
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
            # Union two sets (no repeats)
            # import AniList
            second_list=[]
            response=await get_aniList('woahs')

            # response = requests.post(url, json={'query': query, 'variables': variables})
            list_data=response.get("data").get("MediaListCollection").get('lists')


            for ani_lists in list_data:
                for anime in ani_lists.get("entries"):
                    second_list.append(anime.get("media").get("title").get("english"))

            in_first=set(anime_list)
            in_second=set(second_list)
            in_second_but_not_in_first=in_second - in_first
            anime_list=anime_list + list(in_second_but_not_in_first)

        self.participants=p_list
        self.aniList_personal=anime_list
        # RANDO ANIME CHOOSING CODE HERE
        self.animeQueue=Queue(self.rounds)
        for x in range(self.rounds):
                song_name=self.aniList_personal.pop(randrange(len(self.aniList_personal) - 1))
                if(song_name != None):
                    res=await get_aniListAnime(song_name)
                    anime_data=res.get("data").get("Media")
                    name_types = []
                    name_types.append(anime_data.get('title').get('english'))
                    name_types.append(anime_data.get('title').get('romaji'))
                    name_types.append(anime_data.get('title').get('native'))
                    pic_url=anime_data.get('coverImage').get('medium')
                    site_url=anime_data.get('siteUrl')
                    desc=anime_data.get('description')
                    self.animeQueue.put(Song(anime_data.get('title').get('english'), name_types, pic_url, site_url, desc))

    async def play_game(self):
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
                except Exception:
                    await self.text_channel.send("Error in getting URL", delete_after=5)
                    continue
                await self.text_channel.send("Playing Song", delete_after=5)
                print(current_song.english_name)

            channel=self.text_channel

            msg = await channel.send('Send me that \U0001f44e reaction, to skip', delete_after=self.time_per_song)
            await msg.add_reaction('\U0001f44e')

            def check(reaction, user):
                return str(reaction.emoji) == '\U0001f44e' and user.id != self.bot.user.id

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
                        # print(in_first)
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
        temp_embed.description=current_song.description
        await self.text_channel.send("The correct answer is: ", embed=temp_embed, delete_after=10)

    async def end_game(self):
        # remove the commands
        self.bot.remove_cog(self)
        # send answer
        temp_embed=discord.Embed()
        temp_embed.title="Anime Music Quiz Results"
        temp_embed.color=4652906
        for players in self.participants:
            temp_embed.add_field(name=players.name, value="Score: " + str(players.score), inline="false")
        await self.text_channel.send(embed=temp_embed)

    @commands.command(aliases=['g'])
    async def guess(self, ctx, *guess):
        search = ' '.join(guess)
        for players in self.participants:
            if(players.id == ctx.message.author.id):
                players.guess = search

    @commands.command(aliases=['s'])
    async def search(self, ctx, *anime):
        search = ' '.join(anime)

        res = await get_aniListAnime(search)
        # if there is a response
        if(res != None or res.get("data") != None):
            anime_data = res.get("data").get("Media")
            anime_data.get('title').get('english')
            anime_data.get('title').get('romaji')
            await self.text_channel.send("Did you mean: {} or {}".format(anime_data.get('title').get('english'), anime_data.get('title').get('romaji')), delete_after=10)
        else:
            await self.text_channel.send("No search results", delete_after=5)
            
    async def load_stopwords(self, file_name):
        lineList = list()
        # with open(file_name, encoding="utf8") as f:
        lineList = [line.rstrip('\n').upper() for line in open(file_name, encoding="utf8")]
        return lineList
            
class Player():
    def __init__(self, id, name, mention, guess=None):
        self.score = 0
        self.id = id
        self.name = name
        self.mention = mention
        self.guess = guess


class Song():
    def __init__(self, english_name, name: set, picture_url: str, website_url: str, description: str):
        self.name = name
        self.english_name = english_name
        self.picture_url = picture_url
        self.website_url = website_url
        self.description = description

async def get_aniList(user):
    query = query = '''
    query ($userName: String,$forceSingleCompletedList:Boolean) { 
      MediaListCollection (userName:$userName,type: ANIME,forceSingleCompletedList:$forceSingleCompletedList) {
        lists{
            name
            entries{
                media{
                    siteUrl
                    coverImage{
                        medium
                    }
                    title{
                        english
                        romaji
                        native
                    }
                }
            }
        }
      }
    }
    '''

    variables = {
        'userName': user,
        'forceSingleCompletedList': True
    }

    url = 'https://graphql.anilist.co/'
    ret = []
    async with aiohttp.ClientSession() as cs:
        async with cs.request('POST', url, json={'query': query,
                                                 'variables': variables}) as r:
            response = await r.json()  # returns dict

    return response

async def get_aniListAnime(anime_name):
    query = query = '''
    query ($search: String) { 
      Media (search:$search,type: ANIME) {
            siteUrl
            description
            coverImage{
                medium
            }
            title{
                english
                romaji
                native
            }
                
        }
      }
    '''
    variables = {
        'search': anime_name,
    }

    url = 'https://graphql.anilist.co/'
    ret = []
    async with aiohttp.ClientSession() as cs:
        async with cs.request('POST', url, json={'query': query,
                                                 'variables': variables}) as r:
            response = await r.json()  # returns dict

    return response
