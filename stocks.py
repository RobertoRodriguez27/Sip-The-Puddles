import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import json
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plot

# from glom import glom

'''
     Stockify
     Description: get the user's top 5 artists (just 5 for now) and scale them based on top monthly listens. Buy a 'spot' 
     in the current market. wait till end of month to see if you lost spots or gained based on their artist's growth or 
     decrease in popularity. if you go into debt, the spotify irs will come and get ya
     1. Get user's top 5 artists DONE DONE DONE DONE DONE DONE
     2. graph the artists based in popularity DONE DONE DONE DONE 
     3. need to store the user's 'spots' in a database....
        3a. also need to store all user's spots for an artist  *
     4. update spot market... only really need to update spot market for all current user's artists  *
     * more long run investment (:drum: )
 '''


def fix_illegal_folder_name(folder1, folder2):
    if ':' in folder1:
        folder1.replace(':', 'a')
    if ':' in folder2:
        folder2.replace(':', 'a')


def create_and_organize_files(data=None, folder1=None, folder2="", file=None):
    if data is None or folder1 is None or file is None:  # data, folder1 and file must be defined
        raise Exception("Not enough information to create and/or store folder")
    else:
        if folder2 != "":  # if there is a sub-folder, check if exists. if not, create one
            fix_illegal_folder_name(folder1, folder2)
            new_path = f"C:\\Users\\rober\\PycharmScripts\\Sip The Puddles\\{folder1}\\{folder2}"
            if not os.path.exists(new_path):
                os.mkdir(new_path)

        with open(f"{folder1}/{folder2}/{file}", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        with open(f"{folder1}/{folder2}/{file}") as f:
            complete_json_file = json.load(f)

    return complete_json_file


class User(object):
    client_id = None
    client_secret = None
    username = None
    token = None
    sp = None
    points = None

    def validate_token(self, username, scope):
        self.token = util.prompt_for_user_token(username, scope)
        self.sp = spotipy.Spotify(auth=self.token)
        if not self.token:
            raise Exception('token is not valid')

    def __init__(self, client_id, client_secret, username, scope='user-read-currently-playing', *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not client_id or not client_secret or not username:
            raise Exception('Missing either client_id, client_secret, or username')
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        os.environ['SPOTIPY_CLIENT_ID'] = client_id
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
        os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888/callback'
        SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.validate_token(username, scope)

    def users_top_five(self):
        self.validate_token('titooooo27', scope='user-top-read')
        sp = self.sp

        unfiltered_top_five = create_and_organize_files(sp.current_user_top_artists(limit=5, time_range='medium_term'),
                                                        'json data', '', 'top artist.json')
        df_top_five = pd.json_normalize(data=unfiltered_top_five, record_path=['items'])
        df_top_five.pop('external_urls.spotify')
        df_top_five.pop('followers.href')
        # df_top_five.pop('followers.total') # split between if followers or popularity accurately represent
        df_top_five.pop('popularity')  # an artist's popularity. pop uses a different way to calculate
        df_top_five.pop('id')
        df_top_five.pop('genres')
        df_top_five.pop('href')
        df_top_five.pop('images')
        df_top_five.pop('type')
        df_top_five.pop('uri')

        df_top_five = df_top_five.sort_values('followers.total')

        df_top_five.columns = ['artists', 'followers']

        json_top_five = df_top_five.to_json(orient='records')
        parsed = json.loads(json_top_five)
        with open('json data/json top five.json', 'w', encoding='utf-8') as f:
            json.dump(parsed, f, ensure_ascii=False, indent=4)

        plot.figure(figsize=(12, 6))  # set up the plot size and title
        plot.title("Stockify")

        sb.set_theme(style='darkgrid')  # set up the table color and data
        sb.barplot(x="artists", y="followers", data=df_top_five)

        plot.savefig('top_five.jpg')  # save plot image

    def genres(self):

        self.validate_token('titooooo27', scope='user-top-read')
        sp = self.sp

        unfiltered_top_50 = create_and_organize_files(sp.current_user_top_artists(limit=50, time_range='medium_term'),
                                                      'json data', '', 'genres.json')
        with open('json data/top artist.json') as f:
            results = json.load(f)
        # sets makes the json into a data frame and deletes the columns
        df_genres = pd.json_normalize(data=unfiltered_top_50, record_path=['items'])
        # df_genres = pd.json_normalize(results, record_path=['items'])
        df_genres.pop('external_urls.spotify')
        df_genres.pop('followers.href')
        df_genres.pop('followers.total')  # split between if followers or popularity accurately represent
        df_genres.pop('popularity')  # an artist's popularity. pop uses a different way to calculate
        df_genres.pop('id')
        df_genres.pop('href')
        df_genres.pop('images')
        df_genres.pop('type')
        df_genres.pop('uri')
        df_genres.pop('name')

        json_genres = df_genres.to_json(orient='records')
        parsed = json.loads(json_genres)
        with open('json data/json genres.json', 'w', encoding='utf-8') as f:
            json.dump(parsed, f, ensure_ascii=False, indent=4)

        genre_dict = df_genres.to_dict(orient='dict')
        simple_genre = {'rap': 0, 'hip hop': 0, 'rock': 0, 'indie': 0, 'pop': 0, 'punk': 0, 'other': 0}
        for item in genre_dict['genres']:
            for sub_item in genre_dict['genres'][item]:
                if sub_item in simple_genre.keys():
                    simple_genre[sub_item] += 1
                elif sub_item not in simple_genre.keys():
                    simple_genre['other'] += 1
                    # simple_genre[sub_item] = 1
        plot.axis('equal')
        plot.pie(simple_genre.values(), labels=simple_genre.keys(), autopct=None)
        plot.savefig('genres.jpg')
        print()

    def search_artist(self, query=None):
        if not query:
            raise Exception('you need to search an artist')
        sp = self.sp
        unfiltered_results = create_and_organize_files(sp.search(q=query, type='artist'), 'json data', '',
                                                       'search results.json')
        df_results = pd.json_normalize(data=unfiltered_results, record_path=['artists', 'items'])
        df_results.pop('external_urls.spotify')
        df_results.pop('followers.href')
        df_results.pop('followers.total')
        df_results.pop('genres')
        df_results.pop('href')
        df_results.pop('images')
        df_results.pop('type')
        df_results.pop('uri')

        df_results = df_results.set_index('name')

        print(df_results)


pt = User('ef2607b740534db4a708db8b6feb6e2f', '410147f8a9be40fc8630a12ae1ccf0b3', 'titooooo27',
          scope='user-read-recently-played')  # replace with client id, client secret, and username
# pt.users_top_five()
pt.genres()
# pt.search_artist('The Strokes')
