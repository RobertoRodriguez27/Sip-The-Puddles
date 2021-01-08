import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import json
import pandas as pd
import seaborn
import matplotlib.pyplot as plot
import max_heap as rank


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
                self.fix_illegal_folder_name(folder1, folder2)
                new_path = f"C:\\Users\\rober\\PycharmScripts\\Sip The Puddles\\{folder1}\\{folder2}"
                if not os.path.exists(new_path):
                    os.mkdir(new_path)

            with open(f"{folder1}/{folder2}/{file}", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            with open(f"{folder1}/{folder2}/{file}") as f:
                complete_json_file = json.load(f)

        return complete_json_file

    def fix_illegal_folder_name(self, folder1, folder2):
        if ':' in folder1:
            folder1.replace(':', 'a')
        if ':' in folder2:
            folder2.replace(':', 'a')

    def current_song(self):
        sp = self.sp
        cur = sp.current_user_playing_track()
        if not cur:
            raise Exception("no song is playing")
        song_name = self.create_and_organize_files(cur, 'json data', "", 'current song.json')
        artist_id = song_name.get('item').get('artists')[0].get('id')

        self.all_albums = self.get_album_name_and_ids(artist_id)
        # return self.get_album_name_and_ids(artist_id)
        # return song_name.get('item').get('name')
        # return artist_id

    '''
    1. Get the user's recently played songs
        1a. get all the song names and artists from their recently played
    2. Extract the artists with the least popularity (10 lowest ranked popularity from the bunch)
        2a. send to artist_popularity() to find out their popularity and save the data to filter them later
    '''

    # def recently_played_popularity(self):
    #     sp = self.sp
    #     recent_raw = sp.current_user_recently_played(10)
    #     recent_file = self.create_and_organize_files(recent_raw, 'json data', "", 'recent tracks.json')
    #
    #     '''
    #     Getting all artist names. should have 50 artists names should repeat
    #     Artist name and uri is located in:      items/00/track/artists/0  name || id
    #     Song name and popularity is located in: items/00/track            name || popularity
    #     '''
    #     recent_artists_list = []
    #     recent_popularity_list = []
    #     scrambled_dict = recent_file.get('items')
    #     for item in scrambled_dict:
    #         cur_artist = item.get('track')['name']
    #         recent_artists_list.append(cur_artist)
    #
    #         cur_popularity = item.get('track')['popularity']
    #         recent_popularity_list.append(cur_popularity)
    #
    #     artist_pop = pd.DataFrame(
    #         {
    #             'song name': recent_artists_list,
    #             'popularity': recent_popularity_list
    #         }
    #     )
    #     artist_pop.to_csv('excel files/artists popularity.csv')
    #
    #     plot.bar(artist_pop.get('song name'), artist_pop.get('popularity'))
    #     plot.title("Recent Song's Popularity")
    #     plot.xlabel('song names')
    #     plot.ylabel('song popularity')
    #     plot.show()

    # def song_popularity(self):
    #     sp = self.sp
    #     pop = sp.artist('3AA28KZvwAUcZuOKwyblJQ')
    #     artist = self.create_and_organize_files(pop, 'json data', 'artist pop.json')
    #     return artist.get('name')

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

        # get album names and id's
        album_names = []
        # album_ids = []
        albums_score = []
        unfiltered_albums = unfiltered_albums.get('items')
        all_albums = {}
        for item in unfiltered_albums:
            cur_album_name = item['name']

            if cur_album_name not in album_names:  # if the album is repeated, only get the first
                album_names.append(cur_album_name)
                cur_album_ids = item['id']
                # album_ids.append(cur_album_ids)

                # albums_pop[cur_album_name] = self.albums_popularity(cur_album_ids, cur_album_name, artist_id)
                albums_score.append(self.albums_popularity(cur_album_ids, cur_album_name, artist_id))
                all_albums[cur_album_name] = self.albums_popularity(cur_album_ids, cur_album_name, artist_id)

        # practice = {}
        # for name in album_names:
        #     for pop in albums_score:
        #         practice[name] = pop
        #         albums_score.remove(pop)
        # print(len(practice))
        # print(practice)

        # Below organizes all the artist's albums into a csv file with name and popularity
        all_albums = pd.DataFrame(
            {
                'albums name': album_names,
                'album popularity': albums_score
            }
        )
        # print(all_albums)
        # print(all_albums.size)
        return all_albums
        # all_albums.to_csv('excel files/albums popularity.csv')

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

        # frame = pd.json_normalize(unfiltered_songs, max_level=10)
        # print(frame)

        # grab each song's id to later evaluate each song for their pop
        for song in unfiltered_songs:
            song_names.append(song['name'])  # todo: song_names can be deleted. Used to debug when using console
            song_id.append(song['id'])
        # print(f"{song_names}\n{song_id}")

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
        # print(len(song_to_pop.values()))
        # print(song_to_pop)
        return song_to_pop.get('album popularity')  # this is only its popularity in relation to itself. not
        # to other albums

    def make(self):
        tree = rank.Heap(self.all_albums)
        # frame = pd.read_json('json data/7album json/artist albums.json', orient='records')
        # print(frame)


pt = User('ef2607b740534db4a708db8b6feb6e2f', '410147f8a9be40fc8630a12ae1ccf0b3', 'titooooo27',
          scope='user-read-recently-played')
pt.current_song()
pt.make()
