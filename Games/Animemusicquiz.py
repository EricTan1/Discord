# imports
import discord
import asyncio
import json
import sys
import os
import aiohttp
from discord.ext import commands


class Amq(Game):
    ''' This class is responsible for the entire anime music quiz game
    
    '''

    def __init__(self, bot, participants):
        ''' (Amq, discord.Client, List of Strings) -> Amq
        '''
        super().__init__(bot)


    def start_game(self):
        pass
    def end_game(self):
        pass