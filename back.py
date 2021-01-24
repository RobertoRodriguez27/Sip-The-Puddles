import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import json
import pandas as pd
import seaborn
import matplotlib.pyplot as plot
import max_heap as rank


def fix_illegal_folder_name(folder1, folder2):
    if ':' in folder1:
        folder1.replace(':', 'a')
    if ':' in folder2:
        folder2.replace(':', 'a')


class User(object):
    client_id = None
    client_secret = None
    username = None
    token = None
    sp = None
    all_albums = None

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

    def create_and_organize_files(self, data=None, folder1=None, folder2="", file=None):
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

    def current_song(self):
        sp = self.sp
        cur = sp.current_user_playing_track()
        if not cur:
            raise Exception("no song is playing")
        song_name = self.create_and_organize_files(cur, 'json data', "", 'current song.json')
        artist_id = song_name.get('item').get('artists')[0].get('id')

        self.all_albums = self.get_album_name_and_ids(artist_id)

    '''
    1. Get the user's recently played songs
        1a. get all the song names and artists from their recently played
    2. Extract the artists with the least popularity (10 lowest ranked popularity from the bunch)
        2a. send to artist_popularity() to find out their popularity and save the data to filter them later
    '''

    # Binary Tree of Artist's Albums by Popularity #
    '''
    1. get an artists album's popularity
        1a. get_album_name_and_ids(self) gets name and ids of an artists albums
        1b. send over to another method to...
            aa. get popularity of all songs average it and have be popularity of the album
                aaa. looks like albums does not have the popularity of each song in the json file, so must get the
                id of each song individually to reach its popularity, then do plan aa.
            ab. maybe a different thing to do. Be open to new solutions
    2. send to a helper method to organize into a binary tree
    3. draw binary tree
    '''

    # 1
    # 1a.
    def get_album_name_and_ids(self, artist_id):
        self.validate_token('titooooo27', scope='user-read-recently-played')  # idea is that this will make new token with proper scope
        sp = self.sp
        albums = sp.artist_albums(artist_id=artist_id, album_type='album')

        unfiltered_albums = self.create_and_organize_files(albums, 'json data', f"{artist_id[0]}album json",
                                                           'artist albums.json')

        album_names = []
        albums_score = []
        unfiltered_albums = unfiltered_albums.get('items')
        all_albums = {}
        for item in unfiltered_albums:
            cur_album_name = item['name']

            if cur_album_name not in album_names:  # if the album is repeated, only get the first
                album_names.append(cur_album_name)
                cur_album_ids = item['id']

                albums_score.append(self.albums_popularity(cur_album_ids, cur_album_name, artist_id))
                all_albums[cur_album_name] = self.albums_popularity(cur_album_ids, cur_album_name, artist_id)

        # Below organizes all the artist's albums into a csv file with name and popularity
        all_albums = pd.DataFrame(
            {
                'albums name': album_names,
                'album popularity': albums_score
            }
        )
        return all_albums

    # 1b.
    # successfully gets all song names and id's in an album
    # issue: sp.album_tracks(album_id) this does not list a song's pop. So i get all song id's
    # and do sp.tracks(song_id) and get the song pop from there. feels bad, but may be better solution
    def albums_popularity(self, album_id, album_name, artist_id):
        sp = self.sp  # get authenticated token (see __init__)
        album_tracks = sp.album_tracks(album_id)  # get all songs and info from album

        song_names = []
        song_id = []  # 153: creates new folder for this albums song's json files
        unfiltered_songs = self.create_and_organize_files(album_tracks, 'json data', f"{artist_id[0]}album json",
                                                          f"{album_name}.json")
        unfiltered_songs = unfiltered_songs.get('items')  # shifts the position of the object to iterate easier

        # grab each song's id to later evaluate each song for their pop
        for song in unfiltered_songs:
            song_names.append(song['name'])  # todo: song_names can be deleted. Used to debug when using console
            song_id.append(song['id'])

        # since getting json files for all of the songs in an album seems redundant, no json
        # grabs popularity's of each song
        tracks = sp.tracks(song_id)
        tracks = tracks.get('tracks')
        song_to_pop = {}
        cumulative_pop = 0

        # iterate through all songs in the album, extract each song's popularity and find average. This is album's pop
        for info in tracks:
            song_to_pop[info['name']] = info['popularity']
            cumulative_pop += info['popularity']

        song_to_pop['album popularity'] = cumulative_pop / len(song_id)

        return song_to_pop.get('album popularity')  # this is only its popularity in relation to itself. not
        # to other albums

    def make(self):
        tree = rank.Heap(self.all_albums)
        tree.print()


pt = User('ef2607b740534db4a708db8b6feb6e2f', '410147f8a9be40fc8630a12ae1ccf0b3', 'titooooo27',
          scope='user-read-recently-played')
pt.current_song()
pt.make()
