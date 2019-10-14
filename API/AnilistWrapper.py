import aiohttp
import asyncio
from APIWrapper import GameAPIURLWrapper
class AnilistWrapper(GameAPIURLWrapper):
    async def get_aniList(self, user):
        ''' (str) -> Json obj
        takes in a username off anilist and returns a json object with
        of their animelists off anilist.co (for every list such as progress,completed)
        '''
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
            async with cs.request('POST', self.base_url, json={'query': query,
                                                     'variables': variables}) as r:
                response = await r.json()  # returns dict
        return response
    async def get_aniListAnime(self, anime_name):
        ''' (Str) -> JSON Obj
        Takes in an anime name and returns a json object of 
        10 results that might be related or IS the anime name being searched
        '''
        query = query = '''
        query ($search: String) { 
      Page(page: 1, perPage: 10){
        media (search:$search,type: ANIME) {
          bannerImage
          siteUrl
          tags{
            description
          }
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
        '''
        variables = {
            'search': anime_name,
        }
    
        url = 'https://graphql.anilist.co/'
        ret = []
        async with aiohttp.ClientSession() as cs:
            async with cs.request('POST', self.base_url, json={'query': query,
                                                     'variables': variables}) as r:
                response = await r.json()  # returns dict
    
        return response
    async def get_aniListAnime_single(self, anime_name):
        ''' (Str) -> JSON Obj
        Takes in an anime name and returns a json object of 
        1 result that might be related or IS the anime name being searched
        '''
        query = query = '''
        query ($search: String) { 
        Media (search:$search,type: ANIME) {
          bannerImage
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
            async with cs.request('POST', self.base_url, json={'query': query,
                                                     'variables': variables}) as r:
                response = await r.json()  # returns dict
    
        return response
    async def get_user(self, user_name):
        ''' (Str) -> JSON Obj
        Takes in an anime name and returns a json object of 
        1 result that might be related or IS the anime name being searched
        '''
        query = query = '''
        query ($search: String) { 
        User (search:$search) {
          name
          siteUrl
          avatar{
            medium
          }
        
        }
      }
        '''
        variables = {
            'search': user_name,
        }
    
        url = 'https://graphql.anilist.co/'
        ret = []
        async with aiohttp.ClientSession() as cs:
            async with cs.request('POST', self.base_url, json={'query': query,
                                                     'variables': variables}) as r:
                response = await r.json()  # returns dict
    
        return response    