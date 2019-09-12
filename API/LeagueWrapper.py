
class LeagueWrapper:
    def __init__(self, api_key):
        self.api_key = api_key

    async def get_league_stats_queue(self, summoner_name):
        ''' (Str,Str) -> JSON Obj
        Takes in a summoner name and returns a json obj
        List of queuetypes (dict)
        with keys:
        'queueType'
        'tier'
        'rank'
        'summonerName'
        'leaguePoints'
        'wins'
        'losses'
        '''

        name_url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'.format(summonername) + key
        # get the encryted summ id
        async with aiohttp.ClientSession() as cs:
            async with cs.request('GET', name_url) as r:
                response = await r.json()  # returns dict
        encryted_sum_id = response.get('id')
        stats_url = 'https://na1.api.riotgames.com'
        stats_mid_url = '/lol/league/v4/entries/by-summoner/{}'.format(encryted_sum_id)
        key = '?api_key={}'.format(self.api_key)
        stats_url = stats_url + stats_mid_url + key
        # get the stats
        async with aiohttp.ClientSession() as cs:
            async with cs.request('GET', stats_url) as r:
                response_stats = await r.json()  # returns dict
        return response_stats

    
    async def get_league_stats_champ(self, summoner_name):
        ''' 
        '''
        name_url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'.format(summonername) + key
        # get the encryted summ id
        async with aiohttp.ClientSession() as cs:
            async with cs.request('GET', name_url) as r:
                response = await r.json()  # returns dict
        encryted_sum_id = response.get('id')
        stats_url = 'https://na1.api.riotgames.com'
        stats_mid_url = '/lol/champion-mastery/v4/champion-masteries/by-summoner/{}'.format(encryted_sum_id)
        key = '?api_key={}'.format(self.api_key)
        stats_url = stats_url + stats_mid_url + key
        # get the stats
        async with aiohttp.ClientSession() as cs:
            async with cs.request('GET', stats_url) as r:
                response_stats = await r.json()  # returns dict
        return response_stats
