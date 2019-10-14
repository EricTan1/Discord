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
        ''' (BotApiHandler, discord.client,dict,ForniteWrapper,OsuWrapper,
        LeagueWrapper, AnilistWrapper) -> BotApiHandler
        init method for BotApiHandler
        '''
        # {server:{discordid:{games:[list of games],score:int}}}
        self.persona_dict = persona_dict
        self.league_wrapper = league_wrapper
        self.osu_wrapper = osu_wrapper
        self.fortnite_wrapper = fortnite_wrapper
        self.anilist_wrapper = anilist_wrapper
        self.bot = bot
        print(persona_dict)
        
    @commands.command(aliases=['vl'])
    @commands.has_permissions(manage_channels=True)
    async def verifylogin(self, ctx, game: str, member: discord.Member, *username):
        ''' (BotApiHandler, discord.context,str,discord.member,str) -> None
        Logins in for a different user. Admin perms required to verify the person
        logging in
        '''
        username = ' '.join(username)
        # check if server exists in dict
        await self.setup_profile(ctx.guild.id, member.id)
        if(game.upper() in ["LEAGUE", "LOL"] or game.upper() in ["OSU"]):
            # set up league profile
            # check if its valid profile first
            try:
                if(game.upper() in ["LEAGUE", "LOL"]):
                    stats = await self.league_wrapper.get_game_stats(username)
                    # for this game we keep track of wins
                    count = 0
                    # save the current number of wins
                    for queuetypes in stats:
                        count = count + queuetypes.get('wins')
                    # to fix aliases problems
                    game = "LEAGUE"
                elif(game.upper() in ["OSU"]):
                    stats = await self.osu_wrapper.get_game_stats(username)
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
        ''' (BotApiHandler, discord.context) -> None
        Saves persona_dict
        '''
        await self.save_data()
        
    async def save_data(self):
        ''' (BotApiHandler) -> None
        Saves persona_dict
        '''
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
        ''' (BotApiHandler, discord.context,str,str) -> None
        Adds the username of the user for that game in the persona_dict
        '''
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



    async def update_score(self, game, username, curr_wins):
        ''' (BitApiHandler, str, int) -> (int,int)
        returns the difference between the new and the old
        '''
        ret = 0
        count = 0
        if(game.upper() in ["LEAGUE", "LOL"]):
            stats = await self.league_wrapper.get_game_stats(username)
            # for this game we keep track of wins
            # save the current number of wins
            for queuetypes in stats:
                count = count + queuetypes.get('wins')
        elif(game.upper() in ["OSU"]):
            stats = await self.osu_wrapper.get_game_stats(username)
            # for the game we keep track of performance points (PP)
            # go through all the osu game modes and add the pp
            for gamemodes in stats:
                count = count + int(float(gamemodes.get("pp_raw")))

        ret = count - int(float(curr_wins))
        # somehow user has negative wins (not possible) then ret 0
        if(ret < 0):
            ret = 0
        return (ret, count)

    @commands.command(aliases=['stats'])
    async def status(self, ctx, *person: discord.Member):
        # init dict for message
        game_desc = dict()
        # field index counter
        field_count = 0
        # Check if you are refering to yourself or another person
        if(len(person) == 0):
            this_p = ctx.author
        # if multiple people then first person
        else:
            this_p = person[0]
        # check if server/profile exists
        await self.setup_profile(ctx.guild.id, this_p.id)
        # Creating the status message
        temp_embed = discord.Embed()
        temp_embed.title = "{} Profile".format(this_p.name)
        temp_embed.color = 3066993
        # anilist is one liner so it doesnt really clog up space. Add it
        ani_username = await self.get_animelist(ctx.guild.id, this_p.id)
        if(ani_username != None):
            res = await self.anilist_wrapper.get_user(ani_username)
            res = res.get('data').get('User')
            temp_embed.add_field(name="Anilist", value="[{}]({})".format(res.get('name'), res.get('siteUrl')), inline="false")
            field_count = field_count + 1
        tut_desc = "To check game profiles react with the following emoji's\n\U0001f1f1 for League\n\U0001f1f4 for Osu"
        # loop through all the games
        for games in await self.get_games(ctx.guild.id, this_p.id):
            (diff, n_wins) = await self.update_score(games.get("name"), games.get("username"), games.get("wins"))
            multi = 1
            print("DIFF: " + str(diff) + "n_wins: " + str(n_wins))
            if(games.get("name") in ["LEAGUE", "LOL"]):
                q_list = await self.league_wrapper.get_game_stats(games.get("username"))
                stat_desc=await self.format_league_stats(q_list)
                #temp_embed.add_field(name="League of Legends", value=stat_desc, inline="false")
                multi = 10
            elif(games.get("name") in ["OSU"]):
                mode_list = await self.osu_wrapper.get_game_stats(games.get("username"))
                stat_desc = await self.format_osu_stats(mode_list)
                #temp_embed.add_field(name="Osu", value=stat_desc, inline="false")
                multi = 0.5
            games["wins"] = n_wins
            await self.add_currency(ctx.guild.id, this_p.id, diff, multi)
            # setting up entry
            game_desc[games.get("name")] = dict()
            new_dict = game_desc.get(games.get("name"))

            new_dict["desc"] = stat_desc

        temp_embed.description = "Currency: ${}\n".format(await self.get_currency(ctx.guild.id, this_p.id)) + tut_desc
        msg = await ctx.channel.send(embed=temp_embed)
        # for League
        await msg.add_reaction('\U0001f1f1')
        # for Osu
        await msg.add_reaction('\U0001f1f4')


    
        # For toggling which stats
        while(True):
            def check(reaction, user):
                print(str((str(reaction) == '\U0001f1f1' or str(reaction) == '\U0001f1f4') and reaction.count > 1))
                return (str(reaction) == '\U0001f1f1' or str(reaction) == '\U0001f1f4') and reaction.count > 1

            try:
                reaction, user = await self.bot.wait_for('reaction_add',
                                                         timeout=30,
                                                         check=check)
                # print(reaction)
            except asyncio.TimeoutError:
                print("status timed out")
                temp_embed.color = 15158332
                await msg.edit(embed=temp_embed)
                break
            except:
                print("some error")
            else:
                async def setup_game(game):
                    game_desc[game] = dict()
                    new_dict = game_desc.get(game)
                    new_dict["desc"] = "The user hasn't logged in to {} yet".format(game)
                    
                print("pass2")
                if(str(reaction) == '\U0001f1f1'):
                    game_name = "League of Legends"
                    if(game_desc.get("LEAGUE") == None):
                        await setup_game("LEAGUE")
                    stats_desc = game_desc.get("LEAGUE")
                if(str(reaction) == '\U0001f1f4'):
                    game_name = "Osu"
                    if(game_desc.get("OSU") == None):
                        await setup_game("OSU")
                    stats_desc = game_desc.get("OSU")
                if(stats_desc.get("queue") == None):
                    stats_desc["queue"] = field_count
                    field_count = field_count + 1
                    temp_embed.add_field(name=game_name,
                                         value=stats_desc.get("desc"),
                                         inline="false")
                else:
                    # remove the field
                    field_count = field_count - 1
                    temp_queue=stats_desc.get("queue")
                    temp_embed.remove_field(temp_queue)
                    stats_desc["queue"]=None
                    # fix all the queue index
                    for game_dict in game_desc:
                        curr_queue=game_desc.get(game_dict).get("queue")
                        if(curr_queue != None):
                            if(curr_queue > temp_queue):
                                game_desc.get(game_dict)["queue"]=curr_queue - 1
                print("GAME DESC BEING ADDED: " + game_name)
                await msg.edit(embed=temp_embed)
        print("Done status")


    async def setup_profile(self, server_id, user_id):
        ''' (BotApiHandler, str / int, str / int) -> None
        adds the user to the persona list if user_id isnt already in it
        '''
        # check for profile if no profile to make basic and display
        if(self.persona_dict.get(str(server_id)) == None):
            self.persona_dict[str(server_id)]=dict()
        # check if persona profile exists if not set one up
        if(self.persona_dict.get(str(server_id)).get(str(user_id)) == None):
            server_dict=self.persona_dict.get(str(server_id))
            server_dict[str(user_id)]=dict()
            user_dict=server_dict.get(str(user_id))
            user_dict["currency"]=0
            user_dict["games"]=[]

    async def set_profile_game(self, server_id, user_id, game, username, count):
        ''' (BotApiHandler, str/int,str/int,str,str,int) -> None
        adds the game for user_id to the game list
        '''
        person=self.persona_dict.get(str(server_id)).get(str(user_id))
        game_list=person.get("games")
        # wanna check for if the game is already in the list. if it is then remove
        for check_games in game_list:
            if(check_games.get("name") == game):
                game_list.remove(check_games)
        my_dict=dict()
        my_dict["name"]=game
        my_dict["username"]=username
        my_dict["wins"]=count
        game_list.append(my_dict)

    async def get_currency(self, server_id, user_id):
        ''' (BotApiHandler, str/int,str/int) -> int
        fetches the currency for user_id
        '''
        return self.persona_dict.get(str(server_id)).get(str(user_id)).get("currency")

    
    async def add_currency(self, server_id, user_id, value: int, muiltplier):
        ''' (BotApiHandler, str/int,str/int,int,int or float) -> None
        increments the user_id currency by value
        '''
        temp = self.persona_dict.get(str(server_id)).get(str(user_id))["currency"]
        self.persona_dict.get(str(server_id)).get(str(user_id))["currency"] = temp + value * muiltplier
    
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
        ''' (BotApiHandler) -> dict
        returns the persona dict
        '''
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
            await self.add_currency(ctx.guild.id, ctx.author.id, daily_money, 1)
            await ctx.send("Daily claim successful next daily in {}".format(temp_now.strftime("%b %d %Y %I:%M%p")))

        # get the time needed
        else:
            temp_date = datetime_object + timedelta(hours=time_diff)

            ret = temp_date.strftime("%b %d %Y %I:%M%p")
            await ctx.send("Next daily in {}".format(ret))


        print(self.persona_dict)
    @verifylogin.error
    async def verifylogin_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            temp_embed = discord.Embed()
            temp_embed.color = 15158332
            temp_embed.title = "Error"
            temp_embed.description = 'Invalid parameters check out {}help {}'.format(ctx.prefix, str(ctx.command))
            await ctx.send(embed=temp_embed)
    @login.error
    async def login_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            temp_embed = discord.Embed()
            temp_embed.color = 15158332
            temp_embed.title = "Error"
            temp_embed.description = 'Invalid parameters check out {}help {}'.format(ctx.prefix, str(ctx.command))
            await ctx.send(embed=temp_embed)
    @status.error
    async def status_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            temp_embed = discord.Embed()
            temp_embed.color = 15158332
            temp_embed.title = "Error"
            temp_embed.description = 'Invalid discord member mention'
            await ctx.send(embed=temp_embed)