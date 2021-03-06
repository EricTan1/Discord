# imports
import discord
import asyncio
import json
import sys
import os
import aiohttp
from discord.ext import commands
import queue
from random import randrange
from AniList import AniListWrapper
from Game import Game

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
            p_list.append(self.Player(person.id))
            # Union two sets (no repeats)
            second_list = AniListWrapper.get_anilist(person.anilist_user)
            in_first = set(anime_list)
            in_second = set(second_list)
            in_second_but_not_in_first = in_second - in_first
            result = anime_list + list(in_second_but_not_in_first)
        self.participiants = p_list
        self.aniList = anime_list
        # RANDO ANIME CHOOSING CODE HERE
        self.animeQueue = queue(self.rounds)
        for x in range(self.rounds):
            song_name = self.aniList.pop(randrange(len(self.aniList)))
            self.animeQueue.put(self.Song(song_name, "temp", "temp"))

    async def play_game(self):
        
        while (not self.animeQueue.empty()):
            current_song = self.animeQueue.get()
            # play the song
            if(self.text_channel.guild.voice_client != None):
                # if the bot currently has audio on then stop it
                if(self.text_channel.guild.voice_client.is_playing()):
                    self.text_channel.guild.voice_client.stop()
        
                audio_source = discord.FFmpegPCMAudio(await self.music_player.download("test_song", current_song.name + " OPENING"))
            channel = self.text_channel
            await channel.send('Send me that LOL reaction, to skip')
    
            def check(reaction):
                return str(reaction.emoji) == 'LOL'
    
            try:
                reaction = await client.wait_for('reaction_add', timeout=self.time_per_song, check=check)
            except asyncio.TimeoutError:
                await self._calculate_round_results(current_song)
            else:
                await channel.send('Current Song has been skipped LOL')
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
        self.name = 0
        self.picture_url = picture_url
        self.website_url = website_url
