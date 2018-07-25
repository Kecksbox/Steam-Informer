import requests
import urllib
import progressbar
import re
from bs4 import BeautifulSoup
from time import sleep
from tts import generateAudio
import nltk.data
import os
import tempfile
import time
import wave
import json
import logger

import debugger_utility as du


# Global variables
progress_bar = None
downloaded = 0
module_name = 'steamScrapper'  # Specifies the name of the module
app_data_file = 'appData.json'  # Specifies the file where the data of all processed apps are stored
steam_params = dict(
        origin='Chicago,IL',
        destination='Los+Angeles,CA',
        waypoints='Joplin,MO|Oklahoma+City,OK',
        sensor='false'
    )

app_detail_url = 'http://store.steampowered.com/api/appdetails?appids='


def clean_html(raw_html):
    return re.sub(re.compile("<+(?!.*emphasis)(?!.*break).*"), '', raw_html)


def generate_ssml_from_html(html):
    soup = BeautifulSoup(html)

    for x in soup.find_all("h1"):
        x.name = "emphasis"
        x["level"] = "strong"

    for x in soup.find_all("br"):
        x.name = "break"
        x["time"] = "200ms"

    for x in soup.find_all("li"):
        new_html = '<p><break time="200ms"/>' + x.text + ".</p>"
        new_soup = BeautifulSoup(new_html)
        x.replace_with(new_soup.p)

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    tokens = tokenizer.tokenize(' '.join(clean_html(soup.prettify()).split()))

    text_list = [['<speak><emphasis level="moderate">', 0]]
    for token in tokens:
        text_list[-1][1] += len(token)
        if text_list[-1][1] > 1000:
            text_list[-1][0] += '</emphasis></speak>'
            text_list.append(['<speak><emphasis level="moderate">', 0])
        text_list[-1][0] += token

    return text_list


def show_progress(block_num, block_size, total_size):
    global progress_bar
    if progress_bar is None:
        progress_bar = progressbar.ProgressBar(maxval=total_size)
    downloaded = block_num * block_size
    if downloaded < total_size:
        progress_bar.update(downloaded)
    else:
        progress_bar.finish()
        progress_bar = None
        sleep(1)


def fetch(game_id, args=None):

    if isinstance(game_id, int):
        game_id = str(game_id)

    global app_detail_url
    url = app_detail_url + game_id

    game_resources = dict(
        images=[],
        videos=[],
        audio=[None, []]
    )

    global steam_params

    data = requests.get(url=url, params=steam_params).json()

    # *****************************************
    #                Images
    # ****************************************
    if not du.is_debugging_option_enabled(args, "no_image"):
        for x in data[game_id]['data']['screenshots']:
            logger.log_download(x['path_full'], 'Image', module_name)
            game_resources['images'].append(urllib.request.urlretrieve(x['path_full'], None, show_progress)[0])
            if ((args is not None) and "debugging" in args) and ("image_cap" in args["debugging"] and len(game_resources['images']) == args["debugging"]["image_cap"]): # this is copied for videos. We might want to make this a function. [Malte]
                break

    # ****************************************
    #                Videos
    # ****************************************
    if not du.is_debugging_option_enabled(args, "no_video"):
        for x in data[game_id]['data']['movies']:
            logger.log_download(x['webm']['max'], 'Video', module_name)
            game_resources['videos'].append(urllib.request.urlretrieve(x['webm']['max'], None, show_progress)[0])
            if ((args is not None) and "debugging" in args) and ("video_cap" in args["debugging"] and len(game_resources['videos']) == args["debugging"]["video_cap"]):
                break

    # ****************************************
    #                Audio
    # ****************************************
    if not du.is_debugging_option_enabled(args, "no_audio"):
        game_resources['audio'][0] = os.path.join(tempfile.gettempdir(), time.strftime("%Y%m%d-%H%M%S"))+'.wav'
        with wave.open(game_resources['audio'][0], 'wb') as out:
            params_set = 0
            for x in generate_ssml_from_html(data[game_id]['data']['detailed_description']):
                game_resources['audio'][1].append(generateAudio(x[0]))
                with wave.open(game_resources['audio'][1][-1], 'rb') as w:
                    if params_set == 0:
                        out.setparams(w.getparams())
                        params_set = 1
                    out.writeframes(w.readframes(w.getnframes()))
                if ((args is not None) and "debugging" in args) and ("audio_cap" in args["debugging"] and len(game_resources['audio'][1]) == args["debugging"]["audio_cap"]):
                    break

    return game_resources


def init_app_map():
    """This function loads the blacklisted games from 'appData.json' into memory"""

    global app_data_file

    # Load the data of the already processed apps
    if os.path.isfile(app_data_file):
        with open(app_data_file, 'r') as file:
            data = json.load(file)
            if type(data) == dict:
                return data
    return dict()


def set_game_as_processed(game_id):
    """Sets a game specified by its id as processed in the appData.json"""

    # Get the information of the apps we have already processed
    app_map = init_app_map()

    # Check if the app was already processed
    if str(game_id) in app_map:
        logger.log('steamScrapper', 'Game was marked as processed')
    else:
        logger.log('steamScrapper', 'Game not in list, but was marked as processed')

    # Set the game as processed
    app_map[game_id] = 1

    # Write the new data into a file
    with open(app_data_file, 'w') as file:
        json.dump(app_map, file)


def next_game():
    """This function checks all steam apps for the next game that is needed to be processed"""

    global steam_params
    global app_detail_url
    global app_data_file

    # Get all apps from steam
    apps = requests.get(url='http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json',
                        params=steam_params).json()["applist"]["apps"]

    # Get the information of the apps we have already processed
    app_map = init_app_map()

    for app in apps:
        app_id = str(app['appid'])

        # Check if the app was already processed
        if app_id in app_map:
            continue

        # Get the detailed information of the app from steam
        app = requests.get(url=app_detail_url+app_id, params=steam_params).json()[app_id]

        # Check if the data of the app is accessible
        if not app['success']:
            app_map[app_id] = 0  # App is not usable
            continue

        # Check if the app is a game
        if not app['data']['type'] == 'game':
            app_map[app_id] = 0  # App is not usable
            continue

        # Write the new data into a file
        with open(app_data_file, 'w') as file:
            json.dump(app_map, file)
        return app_id
