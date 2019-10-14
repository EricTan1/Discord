from abc import ABC, abstractmethod
import asyncio

class GameAPIWrapper(ABC):
    ''' Abstract class for game api wrappers
    '''
    pass

class GameAPIKeyWrapper(GameAPIWrapper):
    def __init__(self, api_key):
        self.api_key = api_key
    @abstractmethod
    async def get_game_stats(self, ign):
        pass

    
class GameAPIClientWrapper(GameAPIWrapper):
    def __init__(self, client_secret, client_id, uri):
        self.client_secret = client_secret
        self.client_id = client_id
        self.uri = uri
    @abstractmethod    
    async def get_game_stats(self):
        pass
    @abstractmethod
    async def get_access(self):
        pass    

class GameAPIURLWrapper(GameAPIWrapper):
    def __init__(self, url):
        self.url = url
    async def get_game_stats(self, ign):
        pass
