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


class Amq(Game):
    ''' This class is responsible for the entire anime music quiz game
    
    '''

    def __init__(self, bot, participants, text_channel, voice_channel, music_player, rounds=10, time_sec=20.0):
        ''' (Amq, discord.Client, List of Strings, int, double,) -> Amq
        '''
        super().__init__(bot)
        self.rounds = rounds
        self.music_player = music_player
        self.text_channel = text_channel
        self.voice_channel = voice_channel
        self.time_per_song = time_sec
        p_list = []
        anime_list = []
        # initializing the player list
        for person in participants:
            p_list.append(Player(person.id))
            # Union two sets (no repeats)
            #import AniList
            second_list = get_aniList("orange2pick")
            
            in_first = set(anime_list)
            in_second = set(second_list)
            in_second_but_not_in_first = in_second - in_first
            anime_list = anime_list + list(in_second_but_not_in_first)
            print(anime_list)
        self.participiants = p_list
        self.aniList_personal = anime_list
        # RANDO ANIME CHOOSING CODE HERE
        self.animeQueue = Queue(self.rounds)
        for x in range(self.rounds):
            song_name = self.aniList_personal.pop(randrange(len(self.aniList_personal)))
            self.animeQueue.put(Song(song_name, "temp", "temp"))

    async def play_game(self):
        print("playing game")
        while (not self.animeQueue.empty()):
            current_song = self.animeQueue.get()
            # play the song
            if(self.text_channel.guild.voice_client != None):
                # if the bot currently has audio on then stop it
                if(self.text_channel.guild.voice_client.is_playing()):
                    self.text_channel.guild.voice_client.stop()
                await self.text_channel.send("STARTING DOWNLOAD")
                audio_source = discord.FFmpegPCMAudio(self.music_player.download("test_song", current_song.name + " OPENING"))
                await self.text_channel.send("DONE GETTING STREAM URL")
                self.text_channel.guild.voice_client.play(audio_source)
                await self.text_channel.send("PLAYING SONG")
                # TRYING TO TIME OUT HERE
                try:
                    # Wait for the next song. If we timeout cancel the player and disconnect...
                    async with timeout(300):  # 5 minutes...
                        source = await self.queue.get()
                except asyncio.TimeoutError:
                    return self.destroy(self._guild)
                
            channel = self.text_channel
            await channel.send('Send me that \U0001f44e reaction, to skip')

            def check(reaction, user):
                return str(reaction.emoji) == '\U0001f44e'

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=self.time_per_song, check=check)
            except asyncio.TimeoutError:
                await self._calculate_round_results(current_song)
            else:
                await channel.send('Current Song has been skipped \U0001f44e')
            # if the bot currently has audio on then stop it
            if(self.text_channel.guild.voice_client.is_playing()):
                self.text_channel.guild.voice_client.stop()
                
    async def _calculate_round_results(self, current_song):
        # check answers and reward points
        for players in self.participiants:
            if(players.answer != None):
                if(players.answer.upper() == current_song.name.upper()):
                    player.score = player.score + 1
        # send answer
        await self.text_channel.send("The anime was {}".format(current_song.name))


class Player():
    def __init__(self, id):
        self.score = 0
        self.id = id
        self.answer = None


class Song():
    def __init__(self, name: str, picture_url: str, website_url: str):
        self.name = name
        self.picture_url = picture_url
        self.website_url = website_url
def get_aniList(user):
    query = query = '''
    query ($userName: String,$forceSingleCompletedList:Boolean) { 
      MediaListCollection (userName:$userName,type: ANIME,forceSingleCompletedList:$forceSingleCompletedList) {
        lists{
            name
            entries{
                media{
                    bannerImage
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
    response = requests.post(url, json={'query': query, 'variables': variables})
    list_data = response.json().get("data").get("MediaListCollection").get('lists')

    for ani_lists in list_data:
        for anime in ani_lists.get("entries"):
            ret.append(anime.get("media").get("title").get("english"))
    return ret
