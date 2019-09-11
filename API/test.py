import requests
import asyncio
import json


url = 'https://na1.api.riotgames.com'
mid_url = '/lol/league/v4/entries/by-summoner/{}'.format("XwCrfgL_F_dviy8QXtFvNMd3Ty6RE5oRKCfixqY_-l9wTa4")
key = '?api_key={}'.format("RGAPI-30d584d9-f5d4-4696-ae6a-a2ad5d84fb4b")
new_url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'.format("Familia") + key


url = url + mid_url + key
print(url)
response = requests.get(url)

print(response.json())
