# imports
import discord
import asyncio
import json
import sys
import os
import aiohttp
from datetime import datetime
from datetime import timedelta
from discord.ext import commands

class BotApiHandler(commands.Cog):
    '''
    '''
    def __init__(self, bot, persona_dict, fortnite_wrapper=None,
                 osu_wrapper=None, league_wrapper=None, anilist_wrapper=None):
        # {server:{discordid:{games:[list of games],score:int}}}
        self.persona_dict = persona_dict
        self.league_wrapper = league_wrapper
        self.osu_wrapper = osu_wrapper
        self.fortnite_wrapper = fortnite_wrapper
        self.anilist_wrapper = anilist_wrapper
        print(persona_dict)
        
    @commands.command(aliases=['vl'])
    @commands.has_permissions(manage_channels=True)
    async def verifylogin(self, ctx, game: str, member: discord.Member, *username):
        username = ' '.join(username)
        # check if server exists in dict
        await self.setup_profile(ctx.guild.id, member.id)
        if(game.upper() in ["LEAGUE", "LOL"] or game.upper() in ["OSU"]):
            # set up league profile
            # check if its valid profile first
            try:
                if(game.upper() in ["LEAGUE", "LOL"]):
                    stats = await self.league_wrapper.get_league_stats_queue(username)
                    # for this game we keep track of wins
                    count = 0
                    # save the current number of wins
                    for queuetypes in stats:
                        count = count + queuetypes.get('wins')
                    # to fix aliases problems
                    game = "LEAGUE"
                elif(game.upper() in ["OSU"]):
                    stats = await self.osu_wrapper.get_osu_stats(username)
                    # for the game we keep track of performance points (PP)
                    # go through all the osu game modes and add the pp
                    count = 0
                    for gamemodes in stats:
                        count = count + int(float(gamemodes.get("pp_raw")))
                # creating the obj and adding it to the persona dict
                await self.set_profile_game(ctx.guild.id, member.id, game.upper(), username, count)
                # log in successful message
                temp_embed = discord.Embed()
                temp_embed.color = 3066993
                temp_embed.title = "Success"
                temp_embed.description = "Sucessfully logged in"
                await ctx.send(embed=temp_embed)
            except:
                temp_embed = discord.Embed()
                temp_embed.color = 15158332
                temp_embed.title = "Error"
                temp_embed.description = "Invalid name. Please check the name for the game"
                await ctx.send(embed=temp_embed)
        else:
            temp_embed=discord.Embed()
            temp_embed.color=15158332
            temp_embed.title="Error"
            temp_embed.description="Invalid game. Check the supported games"
            await ctx.send(embed=temp_embed)
        print(self.persona_dict)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def save(self, ctx):
        await self.save_data()
        
    async def save_data(self):
        # path to write
        PERSONA_PATH = "Data/persona.json"
        # Get all the info from the linked list and save it
        file = open(PERSONA_PATH, "w")
        data = json.dumps(self.persona_dict)
        file.write(data)
        file.close()
        print("Finished saving data\n")
        
    @commands.command(aliases=['l', 'log'])
    async def login(self, ctx, game, user_name):
        # check if server/profile exists
        await self.setup_profile(ctx.guild.id, ctx.author.id)
        if(game.upper() in ["ANILIST", "ANIMELIST"]):
            # check if its valid username (aka returns something)
            # add it seperate from the list
            res = await self.anilist_wrapper.get_aniList(user_name)
            if(res.get("errors") == None):
                t_dict = self.persona_dict.get(str(ctx.guild.id)).get(str(ctx.author.id))
                t_dict["anilist"] = user_name
                temp_embed = discord.Embed()
                temp_embed.color = 3066993
                temp_embed.title = "Success"
                temp_embed.description = "Sucessfully logged in"
                await ctx.send(embed=temp_embed)
            else:
                temp_embed = discord.Embed()
                temp_embed.color = 15158332
                temp_embed.title = "Error"
                temp_embed.description = "Invalid username"
                await ctx.send(embed=temp_embed)
        else:
            temp_embed = discord.Embed()
            temp_embed.color = 15158332
            temp_embed.title = "Error"
            temp_embed.description = "Invalid game. Check the supported non-verify games"
            await ctx.send(embed=temp_embed)        
        # if it doesnt create a new server and add the profile in


    @commands.command(aliases=['stats'])
    async def status(self, ctx, *person: discord.Member):
        # IS A TUPLE SO INDEX LIKE LIST
        # Check if you are refering to yourself or another person
        if(len(person) == 0):
            this_p = ctx.author
        # if multiple people then first person
        else:
            this_p = person[0]
        # check if server/profile exists
        await self.setup_profile(ctx.guild.id, this_p.id)
        # Creating the status message
        temp_embed=discord.Embed()
        temp_embed.title = "{} Profile".format(this_p.name)
        temp_embed.color = 3066993
        ani_username = await self.get_animelist(ctx.guild.id, this_p.id)
        if(ani_username != None):
            res = await self.anilist_wrapper.get_user(ani_username)
            res = res.get('data').get('User')
            temp_embed.add_field(name="Anilist", value="[{}]({})".format(res.get('name'), res.get('siteUrl')), inline="false")
        # loop through all the games
        if(len(await self.get_games(ctx.guild.id, this_p.id)) != 0):
            temp_embed.description="Currency: ${}".format(await self.get_currency(ctx.guild.id, this_p.id))
            for games in await self.get_games(ctx.guild.id, this_p.id):
                if(games.get("name") in ["LEAGUE", "LOL"]):
                    q_list=await self.league_wrapper.get_league_stats_queue(games.get("username"))
                    stat_desc=await self.format_league_stats(q_list)
                    temp_embed.add_field(name="League of Legends", value=stat_desc, inline="false")
                elif(games.get("name") in ["OSU"]):
                    mode_list = await self.osu_wrapper.get_osu_stats(games.get("username"))
                    stat_desc = await self.format_osu_stats(mode_list)
                    temp_embed.add_field(name="Osu", value=stat_desc, inline="false")
        else:
            temp_embed.description = "Currency: ${}\nEmpty profile! Please check out the 'login' command".format(await self.get_currency(ctx.guild.id, this_p.id))

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
            
    async def set_profile_game(self, server_id, user_id, game, username, count):
        person = self.persona_dict.get(str(server_id)).get(str(user_id))
        game_list = person.get("games")
        # wanna check for if the game is already in the list. if it is then remove
        for check_games in game_list:
            if(check_games.get("name") == game):
                game_list.remove(check_games)
        my_dict = dict()
        my_dict["name"] = game
        my_dict["username"] = username
        my_dict["wins"] = count
        game_list.append(my_dict)

    async def get_currency(self, server_id, user_id):
        ''' (BotApiHandler, str/int,str/int) -> int
        fetches the currency for user_id
        '''
        return self.persona_dict.get(str(server_id)).get(str(user_id)).get("currency")

    
    async def add_currency(self, server_id, user_id, value: int):
        ''' (BotApiHandler, str/int,str/int,int) -> None
        increments the user_id currency by value
        '''
        temp = self.persona_dict.get(str(server_id)).get(str(user_id))["currency"]
        self.persona_dict.get(str(server_id)).get(str(user_id))["currency"] = temp + value
    
    async def get_daily(self, server_id, user_id):
        ''' (BotApiHandler, str/int,str/int) -> None
        gets the daily time of last used daily
        '''
        return self.persona_dict.get(str(server_id)).get(str(user_id)).get("daily")
    async def set_daily(self, server_id, user_id, value):
        ''' (BotApiHandler, str/int,str/int,str) -> None
        sets the daily time of last used daily
        '''
        self.persona_dict.get(str(server_id)).get(str(user_id))["daily"] = value

    async def get_games(self, server_id, user_id):
        ''' (BotApiHandler, str/int,str/int) -> List of dict
        fetches the game list for user_id
        '''
        return self.persona_dict.get(str(server_id)).get(str(user_id)).get("games")
    async def get_animelist(self, server_id, user_id):
        ''' (BotApiHandler, str/int,str/int) -> str
        fetches the anime list for user_id
        '''
        return self.persona_dict.get(str(server_id)).get(str(user_id)).get("anilist")

    async def format_league_stats(self, queue_list):
        ''' (BotApiHandler, list of dict[json obj]) -> Str
        Takes in the ret of LeagueWrapper and format all the stats into
        a single string
        '''
        ret_stats = ""
        # check if the json file exists
        if(queue_list != None and len(queue_list) != 0):
            # Loop through the queue types
            for queuetypes in queue_list:
                ret_stats = ret_stats + queuetypes.get('queueType').replace("_", " ").title() + "\n"
                ret_stats = ret_stats + "{} {}\t{} LP\n".format(queuetypes.get('tier').title(), queuetypes.get('rank'), queuetypes.get('leaguePoints'))
                ret_stats = ret_stats + "Wins: {}\tLoss: {}\n\n".format(queuetypes.get('wins'), queuetypes.get('losses'))
        else:
            ret_stats = "This player does not play any ranked or is a newly created acc"
        return ret_stats

    async def format_osu_stats(self, mode_List):
        ''' (BotApiHandler, list of dict[json obj]) -> Str
        Takes in the ret of OsuWrapper and format all the stats into
        a single string
        '''
        ret_stats = ""
        if(mode_List != None and len(mode_List) != 0):
            for modes in mode_List:
                # Game mode check
                if(modes.get("mode") == 0):
                    ret_stats = ret_stats + "osu!standard\n"
                elif(modes.get("mode") == 1):
                    ret_stats = ret_stats + "osu!taiko\n"
                elif(modes.get("mode") == 2):
                    ret_stats = ret_stats + "osu!catch\n"
                elif(modes.get("mode") == 3):
                    ret_stats = ret_stats + "osu!mania\n"
                # Add Player Level+ Country
                ret_stats = ret_stats + "Level: {} Country: {}\n".format(int(float(modes.get("level"))), modes.get("country"))                 # playcount and playtime
                # converting seconds to Days hours minutes
                seconds = modes.get("total_seconds_played")
                m, s = divmod(int(seconds), 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)                
                ret_stats = ret_stats + "Total Play Time: {}\n".format('{:d}d {:d}h {:02d}m'.format(d, h, m))                # PP and accuracy
                ret_stats = ret_stats + "pp: {}\tAccuracy: {:03.2f}%\n".format(int(float(modes.get("pp_raw"))), float(modes.get("accuracy")))
                # World rank and country Rank
                ret_stats = ret_stats + "Global Ranking: {}\tCountry Ranking: {}\n\n".format(modes.get("pp_rank"), modes.get("pp_country_rank"))
        else:
            ret_stats="Error in retrieving data"
        return ret_stats
 
    async def format_fortnite_stats(self, json_obj):
        pass

    async def get_persona_dict(self):
        return self.persona_dict

    
    @commands.command(aliases=['d'])
    async def daily(self, ctx):
        ''' (BotApiHandler,str) -> None
        Daily command. Gives daily_money to the user.
        20 hour interval for next daily.
        '''
        await self.setup_profile(ctx.guild.id, ctx.author.id)
        # declaring variables and values
        multipler = 1
        daily_money = 200
        # in hours
        time_diff = 20
        # return value
        ret = -1
        # getting the daily timer
        dailyTimer = await self.get_daily(ctx.guild.id, ctx.author.id)
        # turn the string into a dateTime obj if it exists
        if(dailyTimer != None):
            datetime_object = datetime.strptime(dailyTimer, '%b %d %Y %I:%M%p')
        now = datetime.now()
        # check if its been 20 hours or no daily has been ever claimed yet
        if ((dailyTimer == None) or (not (now - timedelta(hours=time_diff) <= datetime_object <= now + timedelta(hours=time_diff)))):
            # if it has then add to the balance
            # set the new dateTime
            temp_now = now + + timedelta(hours=time_diff)
            await self.set_daily(ctx.guild.id, ctx.author.id, now.strftime("%b %d %Y %I:%M%p"))
            await self.add_currency(ctx.guild.id, ctx.author.id, daily_money)
            await ctx.send("Daily claim successful next daily in {}".format(temp_now.strftime("%b %d %Y %I:%M%p")))

        # get the time needed
        else:
            temp_date = datetime_object + timedelta(hours=time_diff)

            ret = temp_date.strftime("%b %d %Y %I:%M%p")
            await ctx.send("Next daily in {}".format(ret))


        print(self.persona_dict)
