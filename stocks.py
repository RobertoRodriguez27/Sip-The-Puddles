import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import json
import pandas as pd
# import seaborn as sb
import matplotlib.pyplot as plot
from user_info import client_secret, client, username
from selenium import webdriver

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


# in the event that a file/folder have an item that windows does not like, change into something acceptable
def fix_illegal_folder_name(folder1, folder2):
    if ':' in folder1:
        folder1.replace(':', 'a')
    if ':' in folder2:
        folder2.replace(':', 'a')


# organizes the json files made and returns a json object back to be turned into a data frame
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
    driver = None

    '''
    validates the user's token so the user can be allowed to change
    the scopes
    '''

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
        # set up selenium
        PATH = 'C:\\Users\\rober\\Downloads\\edgedriver_win32\\msedgedriver.exe'
        self.driver = webdriver.Edge(PATH)

    '''
    gets the user's top 5 artists from the past six months and ranks them based on
    the amount of followers they have. Then sends the dataframe holding the artists and
    their followers to main.py. Using Flask, the data is sent into LandingPage.html
    '''
    def users_top_five(self):
        self.validate_token('titooooo27', scope='user-top-read')
        sp = self.sp

        # makes a json file from the results of the artist's top 5 artists. Then puts it into a df and deletes the
        # columns that are not necessary
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

        # sorts the df from less to greater based on followers.total
        df_top_five = df_top_five.sort_values('followers.total')

        # renames the columns
        df_top_five.columns = ['artists', 'followers']

        # WARNING: using matplotlib is warned against by flask, and it is already not
        # really being utilized, so it is looking to be cut. along with saving the dataframe as a json

        # saves the json file to then be used by home.html and made
        # into a bar graph using chart.js
        json_top_five = df_top_five.to_json(orient='records')
        parsed = json.loads(json_top_five)
        with open('json data/json top five.json', 'w', encoding='utf-8') as f:
            json.dump(parsed, f, ensure_ascii=False, indent=4)

        # since the data is being sent directly to the web page using flask
        # plot.figure(figsize=(12, 6))  # set up the plot size and title
        # plot.title("Stockify")
        #
        # sb.set_theme(style='darkgrid')  # set up the table color and data
        # sb.barplot(x="artists", y="followers", data=df_top_five)
        #
        # plot.savefig('top_five.jpg')  # save plot image
        return df_top_five  # return the dataframe containing the artist names and their followers

    '''
    GOAL: Top 5 artists but based of their monthly listeners
        1) get the user's top artists, more importantly for their id's
        2) add the artist id to the search
        3) using selenium, webscrape the artist's monthly listeners
        4) repeat until containing top 5 of the user's 
    ISSUES:
        1) takes the webpage a while to load since this will need to perform a webscrape
        2) reloading page will cause issue 1 (storing values after first scraping and doing a try/catch and solve this)
        3) web page is 'fragile.' can fail relatively easily (assuming has to do with scraping)
        4) if UI changes, this falls apart
        5) how can i make this run for other users since they will not have an edge webdriver (for scraping)
            5a) possible and somehow even more stupid(?) solution: create a separate project that runs this 
            method ~1 a week for as many artists as possible and enter it into a db. then on this project, perform
            queries to the db to grab that information. will make the site more stable (at least i think) and will
            make it faster 
    SUCCESSES:
        1) iterates through the user's top 5 and grabs the monthly listeners
        2) users will be able to see something that better represents the artists popularity
        3) does actually fluctuate over time
        4) makes me kind of proud
    OVERALL:
        I am not too sure if this is a good solution, however, I don't really see a viable reason to stop since
        this is more for my own learning. I will have to think over implementing 5a is really going to be worth it.
    '''
    def top_monthly(self):
        # 1)
        self.validate_token('titooooo27', scope='user-top-read')
        sp = self.sp

        # makes a json file from the results of the artist's top 5 artists. Then puts it into a df and deletes the
        # columns that are not necessary
        unfiltered_top_monthly = create_and_organize_files(
            sp.current_user_top_artists(limit=5, time_range='medium_term'), 'json data', '', 'top monthly.json')
        df_top_monthly = pd.json_normalize(data=unfiltered_top_monthly, record_path=['items'])
        df_top_monthly.pop('external_urls.spotify')
        df_top_monthly.pop('followers.href')
        df_top_monthly.pop('followers.total')
        df_top_monthly.pop('popularity')
        # df_top_monthly.pop('id')
        df_top_monthly.pop('genres')
        df_top_monthly.pop('href')
        df_top_monthly.pop('images')
        df_top_monthly.pop('type')
        df_top_monthly.pop('uri')
        # 2 - 4) side note class with monthly is _85aaee9fc23ca61102952862a10b544c-scss
        listeners = []
        for id in df_top_monthly['id']:  # 4)
            self.driver.get(f'https://open.spotify.com/artist/{id}')  # 2)
            self.driver.implicitly_wait(3)
            monthly = self.driver.find_element_by_class_name(
                '_85aaee9fc23ca61102952862a10b544c-scss').get_attribute('innerHTML').splitlines()[0]  # 3)

            monthly_num = monthly.split(' ')[0]  # clean the monthly listeners so only the integer remains
            monthly_num = monthly_num.replace(',', '')
            listeners.append(int(monthly_num))  # enters only the numbers into the monthly listeners

        df_top_monthly['monthly listeners'] = listeners  # add the artists monthly listeners to the dataframe
        df_top_monthly.pop('id')  # pop off the id. no longer relevant
        df_top_monthly.columns = ['artists', 'monthly listeners']
        return df_top_monthly

    '''
    Gets the user's top 50 artists and extracts the genres
    TODO: also need to find a way to get genres in a cleaner way and be able to get the sub genres
    and group them into their umbrella genre. EX: 'underground hip hop' should only count as 'hip hop'
    TODO: With the json file of the results, I want to send it over to home.html so it can become a 
    chart using chart.js
    '''
    def genres(self):

        self.validate_token('titooooo27', scope='user-top-read')
        sp = self.sp

        unfiltered_top_50 = create_and_organize_files(sp.current_user_top_artists(limit=50, time_range='medium_term'),
                                                      'json data', '', 'genres.json')

        # sets makes the json into a data frame and deletes the columns
        df_genres = pd.json_normalize(data=unfiltered_top_50, record_path=['items'])
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

        # saves a json file of the wanted information. this is to be used by the home.html to
        # create a pie chart using chart.js
        json_genres = df_genres.to_json(orient='records')
        parsed = json.loads(json_genres)
        with open('json data/json genres.json', 'w', encoding='utf-8') as f:
            json.dump(parsed, f, ensure_ascii=False, indent=4)

        # grabs the genres from the user's most listened artists and counts them
        # TODO: need to check if one of the 'simple_genres' is a substring of the artists' genres
        # TODO: this will allow a more accurate representation of the genres a user listens to without
        # TODO: having an excess of sub genres
        genre_dict = df_genres.to_dict(orient='dict')
        simple_genre = {'rap': 0, 'hip hop': 0, 'rock': 0, 'indie': 0, 'pop': 0, 'punk': 0, 'other': 0}
        for item in genre_dict['genres']:
            for sub_item in genre_dict['genres'][item]:
                if sub_item in simple_genre.keys():
                    simple_genre[sub_item] += 1
                elif sub_item not in simple_genre.keys():
                    simple_genre['other'] += 1
                    # simple_genre[sub_item] = 1

        # creates a pie chart of the genres. Currently over powered by 'other' due to excess of sub genres
        plot.axis('equal')
        plot.pie(simple_genre.values(), labels=simple_genre.keys(), autopct=None)
        plot.savefig('genres.jpg')

    '''
    User places a bet on an artist they like. they also put down how long the 
    bet will take place for 
    '''

    def bets(self):
        pass

    '''
    Search feature. uses the artist query to find the 5 closest artists to the query
    and returns their name, popularity, and artist id
    '''

    def search_artist(self, query=None):
        if not query:
            raise Exception('you need to search an artist')
        sp = self.sp

        # makes a json file from the results the search. Then puts it into a df and deletes the
        # columns that are not necessary
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

    '''
    How to get the top 10 most popular artists when spotify and spotipy do not do that
    One way to do that can be to get the most popular songs and checking (somehow) if 
    they are in the top 10 range. I don't think spotify API will notify if in ranked globably category
    
    Second way can be to manually find the rank 10 person then find the artists that have b.b
    '''


pt = User(client, client_secret, username,
          scope='user-read-recently-played')  # replace with client id, client secret, and username
# pt.users_top_five()
pt.top_monthly()
# pt.genres()
# pt.search_artist('The Strokes')
