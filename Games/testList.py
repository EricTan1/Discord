import requests

query = query = '''
query ($userName: String,$forceSingleCompletedList:Boolean) { 
  MediaListCollection (userName:$userName,type: ANIME,forceSingleCompletedList:$forceSingleCompletedList) {
    lists{
        name
        entries{
            media{
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

# Define our query variables and values that will be used in the query request
variables = {
    'id': 15125
}
variables = {
    'userName': 'Orange2Pick',
    'forceSingleCompletedList': True
}


url = 'https://graphql.anilist.co/'

response = requests.post(url, json={'query': query, 'variables': variables})
print(response.json())
