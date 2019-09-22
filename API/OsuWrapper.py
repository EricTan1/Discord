import aiohttp
import asyncio

class OsuWrapper:
    def __init__(self, api_key):
        self.api_key = api_key
    async def get_osu_stats(self, osu_name):
        ''' (OsuWrapper,Str) -> JSON Obj
        Takes in a osu name or id and returns a json obj
        List of of users
        with keys:
        "username"
        "playcount"
        "pp_rank"
        "level"
        "pp_raw"
        "accuracy"
        "country"
        "total_seconds_played"
        "pp_country_rank"
        "mode" (0-4) for osu gamemodes
        '''
        stats_url_base = 'https://osu.ppy.sh'
        key = '&k={}'.format(self.api_key)
        ret_list = []

        # get the stats
        async with aiohttp.ClientSession() as cs:
            # Check all modes
            for index in range(4):
                stats_mid_url = '/api/get_user?u={}&m={}'.format(osu_name, index)
                stats_url = stats_url_base + stats_mid_url + key
                async with cs.request('GET', stats_url) as r:
                    response_stats = await r.json()
                print("done getting osu info")
                game_info = response_stats[0]
                # print(game_info)
                #  if pp_raw is none then player doesnt play gamemode. o/w add it
                if(game_info.get("pp_raw") != None):
                    game_info["mode"] = index
                    ret_list.append(response_stats[0])
                    print("done checking osu info")
        return ret_list
