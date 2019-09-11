from abc import ABC, abstractmethod
class Game(ABC):
    ''' This is an Abstract base class representing a game for the discord bot
    '''
 
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
    
    @abstractmethod
    def play_game(self):
        pass
