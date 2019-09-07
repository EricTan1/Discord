import requests
import asyncio
import json

def get_aniList(user):
      query = query = '''
      query ($userName: String,$forceSingleCompletedList:Boolean) { 
        MediaListCollection (userName:$userName,type: ANIME,forceSingleCompletedList:$forceSingleCompletedList) {
          lists{
              name
              entries{
                  media{
                      bannerImage
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
      response = requests.post(url, json={'query': query, 'variables': variables})
      list_data = response.get("data").get("MediaListCollection").get('lists')

      for ani_lists in list_data:
            for anime in ani_lists.get("entries"):
                  ret.append(anime.get("media").get("title").get("english"))
      return r
