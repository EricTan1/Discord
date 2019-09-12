# imports
import discord
import asyncio
import json
import sys
import os
import aiohttp
from discord.ext import commands

class BotApiHandler(commands.Cog):
    def __init__(self, bot, persona_dict, fortnite_wrapper=None,
                 osu_wrapper=None, league_wrapper=None):
        # {server:{discordid:{games:[list of games],score:int}}}
        self.persona_dict = persona_dict
        self.league_wrapper = league_wrapper
        self.osu_wrapper = osu_wrapper
        self.fortnite_wrapper = fortnite_wrapper
        print(persona_dict)
        
    @commands.command(aliases=['vl'])
    @commands.has_permissions(manage_channels=True)
    async def verifylogin(self, ctx, game: str, member: discord.Member, username):
        # check if server exists in dict
        await self.setup_profile(ctx.guild.id, member.id)
        if(game.upper() in ["LEAGUE", "LOL"]):
            # set up league profile
            # check if its valid profile first
            try:
                stats = await self.league_wrapper.get_league_stats_queue(username)
                wins = 0
                # save the current number of wins
                for queuetypes in stats:
                    wins = wins + queuetypes.get('wins')
                await self.set_profile_league(ctx.guild.id, member.id, username, wins)
                temp_embed = discord.Embed()
                temp_embed.color = 3066993
                temp_embed.title = "Success"
                temp_embed.description = "Sucessfully loggined in"
                await ctx.send(embed=temp_embed)                
            except:
                temp_embed = discord.Embed()
                temp_embed.color = 15158332
                temp_embed.title = "Error"
                temp_embed.description = "Invalid summoner name"
                await ctx.send(embed=temp_embed)
        else:
            temp_embed = discord.Embed()
            temp_embed.color = 15158332
            temp_embed.title = "Error"
            temp_embed.description = "Invalid game. Check the supported games"
            await ctx.send(embed=temp_embed)
        print(self.persona_dict)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def save(self, ctx):
        # path to write
        PERSONA_PATH = "Data/persona.json"
        # Get all the info from the linked list and save it
        file = open(PERSONA_PATH, "w")
        data = json.dumps(self.persona_dict)
        file.write(data)
        file.close()
        print("Finished saving data\n")        

    @commands.command(aliases=['l'])
    async def login(self, ctx, game, user_name):
        # check if server/profile exists
        await self.setup_profile(ctx.guild.id, ctx.author.id)
        if(game.upper() in ["anilist", "animelist"]):
            pass
        else:
            temp_embed = discord.Embed()
            temp_embed.color = 15158332
            temp_embed.title = "Error"
            temp_embed.description = "Invalid game. Check the supported games"
            await ctx.send(embed=temp_embed)        
        # if it doesnt create a new server and add the profile in


    @commands.command(aliases=['stats'])
    async def status(self, ctx, *person):
        if(len(person) == 0):
            # check if server/profile exists
            await self.setup_profile(ctx.guild.id, ctx.author.id)
            # Creating the status message
            temp_embed=discord.Embed()
            temp_embed.title="{} Profile".format(ctx.message.author.name)
            temp_embed.color=3066993
            # loop through all the games
            if(len(await self.get_games(ctx.guild.id, ctx.author.id)) != 0):
                temp_embed.description = "Currency: ${}".format(await self.get_currency(ctx.guild.id, ctx.author.id))
                for games in await self.get_games(ctx.guild.id, ctx.author.id):
                    if(games.get("name") == "LEAGUE"):
                        q_list=await self.league_wrapper.get_league_stats_queue(games.get("username"))
                        print(q_list)
                        stat_desc=await self.format_league_stats(q_list)
                        temp_embed.add_field(name="League of Legends", value=stat_desc, inline="false")
            else:
                temp_embed.description = "Currency: ${}\nEmpty profile! Please check out the 'login' command".format(await self.get_currency(ctx.guild.id, ctx.author.id))

            await ctx.send(embed=temp_embed)

    async def setup_profile(self, server_id, user_id):
        # check for profile if no profile to make basic and display
        if(self.persona_dict.get(str(server_id)) == None):
            self.persona_dict[str(server_id)]=dict()
        # check if persona profile exists if not set one up
        if(self.persona_dict.get(str(server_id)).get(str(user_id)) == None):
            server_dict=self.persona_dict.get(str(server_id))
            server_dict[str(user_id)]=dict()
            user_dict=server_dict.get(str(user_id))
            user_dict["currency"]=0
            user_dict["games"] = []
        print(self.persona_dict)

    async def set_profile_league(self, server_id, user_id, username, wins):
        person = self.persona_dict.get(str(server_id)).get(str(user_id))
        game_list = person.get("games")
        my_dict = dict()
        my_dict["name"] = "LEAGUE"
        my_dict["username"] = username
        my_dict["wins"] = wins
        game_list.append(my_dict)
        
    async def get_currency(self, server_id, user_id):
        return self.persona_dict.get(str(server_id)).get(str(user_id)).get("currency")

    async def get_games(self, server_id, user_id):
        return self.persona_dict.get(str(server_id)).get(str(user_id)).get("games")
    
    async def format_league_stats(self, queue_list):
        ''' (BotApiHandler, list of dict[json obj])-> Str or None
        '''
        ret_stats = ""
        # check if the json file exists
        if(queue_list != None):
            # Loop through the queue types
            for queuetypes in queue_list:
                ret_stats = ret_stats + queuetypes.get('queueType').replace("_", " ") + "\n"
                ret_stats = ret_stats + "{} {} {} LP\n".format(queuetypes.get('tier'), queuetypes.get('rank'), queuetypes.get('leaguePoints'))
                ret_stats = ret_stats + "Wins: {} Loss: {}\n\n".format(queuetypes.get('wins'), queuetypes.get('losses'))
        else:
            ret_stats = None
        return ret_stats

    async def format_osu_stats(self, json_obj):
        pass
 
    async def format_fortnite_stats(self, json_obj):
        pass

    async def get_persona_dict(self):
        return self.persona_dict
