'''
Utilty class to handle blizzard api requests
'''

# setup and python utility
from dotenv import load_dotenv, find_dotenv
import requests
import os

# env handling
load_dotenv(find_dotenv())

# local utility
#from utility.database import RelsieDB

# logging
import logging
logger = logging.getLogger(__name__)


class BlizzardAPI:


    def __init__(self):
        self._session = requests.Session()

        self._client_id = os.environ.get("BLIZZARD_API_CLIENT_ID")
        self._client_secret = os.environ.get("BLIZZARD_API_CLIENT_SECRET")
        self._access_token = self.create_access_token(self._client_id, self._client_secret).get("access_token")

        print(f"access token: {self._access_token}")

        self._api_url = "https://{0}.api.blizzard.com{1}"

    
    def create_access_token(self, client_id, client_secret, region = 'us'):
        data = {'grant_type': 'client_credentials'}
        response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))

        return self._response_handler(response)

    
    def _response_handler(self, response):
        
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            print("Could not decode: ", response.text, f" >> ERROR: {e}")
    
    
    def _request_handler(self, url, region, query_params):
        if query_params.get("access_token") is None:
            query_params["access_token"] = self._access_token
        
        print(url)

        response = self._session.get(url, params=query_params)

        return self._response_handler(response)
    

    def _format_api_url(self, resource, region):
        # format the blizzard api url and return it
        url = self._api_url.format(region, resource)
        return url
        
    
    # non-internal-only method ("public" facing)
    def get_resource(self, resource, region, query_params = {}):
        # interpret the resource (url .. /data/character/ etc.) and get the response
        url = self._format_api_url(resource, region)
        return self._request_handler(url, region, query_params)


bapi = BlizzardAPI()

resource = "/profile/wow/character/statistics/Chumpjohn"
region = "us"
locale = "en_US"

query_params = {"namespace": f"static-classic-{region}", "locale": locale}
print(bapi.get_resource(resource, region, query_params))