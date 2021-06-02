import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import requests
import pandas as pd
from personal.user_info import client_secret, client, username


class Rework(object):
    client_id = None
    client_secret = None
    username = None
    token = None
    sp = None
    points = None
    api_req = 'https://api.t4ils.dev/'

    def __init__(self, client_id, client_secret_id, username, scope='user-read-currently-playing', *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not client_id or not client_secret_id or not username:
            raise Exception('Missing either client_id, client_secret, or username')
        self.client_id = client_id
        self.client_secret = client_secret_id
        self.username = username
        os.environ['SPOTIPY_CLIENT_ID'] = client_id
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret_id
        os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888/callback'
        SpotifyClientCredentials(client_id=client_id, client_secret=client_secret_id)
        self.validate_token(username, scope)

    def validate_token(self, username, scope):
        self.token = util.prompt_for_user_token(username, scope)
        self.sp = spotipy.Spotify(auth=self.token)
        if not self.token:
            raise Exception('token is not valid')

    def rework_monthly(self):
        endpoint = 'artistInfo?artistid='
        self.validate_token(username=username, scope='user-top-read')
        sp = self.sp

        unfiltered_top_monthly = sp.current_user_top_artists(limit=5, time_range='medium_term')

        art_names, art_ids, listeners = [], [], []
        for item in unfiltered_top_monthly['items']:
            art_names.append(item['name'])
            art_ids.append(item['id'])

            link = self.api_req + endpoint + item['id']
            response = requests.get(link)
            raw = response.json()
            number = int(raw['data']['monthly_listeners']['listener_count'])
            listeners.append(number)

        df = pd.DataFrame(list(zip(art_names, listeners)), columns=['artists', 'monthly listeners'])
        return df

    def polls(self):
        pass


# re = Rework(client, client_secret, username)
# re.rework_monthly()

