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
        "user_id"
        "username"
        "join_date"
        "count300"
        "count100"
        "count50"
        "playcount"
        "ranked_score"
        "total_score"
        "pp_rank"
        "level"
        "pp_raw"
        "accuracy"
        "count_rank_ss"        
        "count_rank_ssh"       
        "count_rank_s"         
        "count_rank_sh"
        "count_rank_a"
        "country"
        "total_seconds_played"
        "pp_country_rank"

        '''
        key = '&k={}'.format(self.api_key)
        stats_url = 'https://osu.ppy.sh'
        stats_mid_url = '/api/get_user?u={}'.format(osu_name)
        stats_url = stats_url + stats_mid_url + key
        # get the stats
        async with aiohttp.ClientSession() as cs:
            async with cs.request('GET', stats_url) as r:
                response_stats = await r.json()  # returns dict
        return response_stats    