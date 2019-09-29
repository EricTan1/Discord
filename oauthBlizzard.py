import requests
class Oauth(object):
    client_id = "some client id here"
    client_secret = "some client secret here"
    scope = "openid"
    redirect_uri = "http://127.0.0.1:5000/login"
    #permissions = "3147776"
    response_type = "code"
    region = "US"
    #state = "JSON"
    blizzard_login_url = "https://{}.battle.net/oauth/authorize?client_id={}&scope={}&redirect_uri={}&response_type={}".format(region, client_id, scope, redirect_uri, response_type)
    
    blizzard_token_url = "https://{}.battle.net/oauth/token".format(region)
    blizzard_api_url = "https://{}.battle.net".format(region)
    blizzard_gameapi_url = "https://{}.api.blizzard.com".format(region)
    @staticmethod
    def get_access_token(code):
        data = {
          'client_id': Oauth.client_id,
          'client_secret': Oauth.client_secret,
          'grant_type': 'authorization_code',
          'code': code,
          'redirect_uri': Oauth.redirect_uri
        }
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url=Oauth.blizzard_token_url, data=data, headers=headers)
        # r.raise_for_status()
        return r.json()
    @staticmethod
    def refresh_token(refresh_token):
        data = {
          'client_id': Oauth.client_id,
          'client_secret': Oauth.client_secret,
          'grant_type': 'refresh_token',
          'refresh_token': refresh_token,
          'redirect_uri': Oauth.redirect_uri,
          'scope': 'identify guilds'
        }
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(url=Oauth.discord_token_url, data=data, headers=headers)
        # r.raise_for_status()
        return r.json()
    @staticmethod
    def get_user_json(access_token):
        url = Oauth.blizzard_api_url + "/oauth/userinfo"
        headers = {
            "Authorization": "Bearer {}".format(access_token)
        }
        r = requests.get(url=url, headers=headers)
        return r.json()
    @staticmethod
    def get_wow_profile(access_token):
        url = Oauth.blizzard_gameapi_url + "/wow/user/characters?access_token={}".format(access_token)
        headers = {
            "Accept": "application/json"
        }
        r = requests.get(url=url, headers=headers)
        return r.json()
    @staticmethod
    def get_sc2_profile(access_token, profileID):
        url = Oauth.blizzard_gameapi_url + "/sc2/profile/:regionID/:realmID/{}?:regionId={}&:realmId={}&locale=en_US&access_token={}".format(profileID, 1, 1, 1, access_token)
        headers = {
            "Accept": "application/json"
        }
        r = requests.get(url=url, headers=headers)
        return r.json()  

