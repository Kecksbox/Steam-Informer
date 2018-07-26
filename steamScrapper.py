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


def get_images(game_data, image_limit=-1):
    """This function downloads and saves images of a specified game the amount of images downloaded can be limited"""

    # Check if there are images for the game
    if 'screenshots' not in game_data['data']:
        logger.log('There are no images for this game', module_name)
        return None

    # Get the amount of images
    image_count = len(game_data['data']['screenshots'])

    # Get urls of the images
    game_image_urls = game_data['data']['screenshots']

    # Get a dict ready to save the images
    game_images = []

    # Limit the images which will be processed if set
    if (image_limit > -1) and (image_limit < image_count):
        image_count = image_limit

    # Download the target amount of images
    for image_index in range(image_count):

        # Load a single image
        image = game_image_urls[image_index]

        # Log the download information
        logger.log_download(image['path_full'], 'Image', module_name)

        # Download the image and save it
        game_images.append(urllib.request.urlretrieve(image['path_full'], None, show_progress)[0])

    # Return the images (paths to the images, located in tmp)
    return game_images


def get_videos(game_data, video_limit=-1):
    """This function downloads and saves videos of a specified game the amount of videos downloaded can be limited"""

    # Check if there are videos for the game
    if 'movies' not in game_data['data']:
        logger.log('There are no videos for this game', module_name)
        return None

    # Get the amount of videos
    video_count = len(game_data['data']['movies'])

    # Get the urls of the videos
    game_video_jsons = game_data['data']['movies']

    # Get a dict ready to save the videos
    game_videos = []

    # Limit the videos which will be processed if set
    if (video_limit > -1) and (video_limit < video_count):
        video_count = video_limit

    # Download the target amount of videos
    for video_index in range(video_count):

        # Load a single video
        video = game_video_jsons[video_index]

        # Log the download information
        logger.log_download(video['webm']['max'], 'Video', module_name)

        # Download the video and save it
        game_videos.append(urllib.request.urlretrieve(video['webm']['max'], None, show_progress)[0])

    # Return the videos (paths to the videos, located in tmp)
    return game_videos


def get_audio(game_data):
    """This function converts the description text of a game into an audio file via TTS"""

    # Check if there is a description
    if 'detailed_description' not in game_data['data']:
        logger.log('There is no detailed description for this game', module_name)
        return None

    # Set the name of the audio file
    audio_file_name = os.path.join(tempfile.gettempdir(), time.strftime("%Y%m%d-%H%M%S")) + '.wav'

    # Get a dict ready to save the audio
    audio_clips = []

    # Get a variable ready to save the final file
    audio_clip = audio_file_name

    # Create the audio clips
    with wave.open(audio_file_name, 'wb') as complete_audio:

        # Set the params to not set
        params_set = 0

        # Get the ssml for each text
        for text in generate_ssml_from_html(game_data['data']['detailed_description']):

            # Create the audio for each text
            audio_clips.append(generateAudio(text[0]))

            # Write the partial audio clips
            with wave.open(audio_clips[-1], 'rb') as partial_audio:

                # If the params arn´t set, set them
                if params_set == 0:
                    complete_audio.setparams(partial_audio.getparams())
                    params_set = 1

                # Write the partial audio into the complete audio clip
                complete_audio.writeframes(partial_audio.readframes(partial_audio.getnframes()))

    # Return the audio (path to the audio, located in tmp)
    return [audio_clip, audio_clips]


def fetch(game_id, params=None):
    """Fetches images, videos and generates audio from the description of a game"""

    # Global variables
    global app_detail_url
    global steam_params

    # Convert the id to string
    if isinstance(game_id, int):
        game_id = str(game_id)

    # The url to get detailed information about a game via the steam api
    url = app_detail_url + game_id

    # Dict to save all the fetched data
    game_resources = dict(
        images=[],
        videos=[],
        audio=[None, []]
    )

    # Get the data of a specific game
    data = requests.get(url=url, params=steam_params).json()

    # Set the limit parameters
    image_limit = -1
    video_limit = -1
    no_audio = False

    # Set the image limits if set in the params
    if 'image_limit' in params:
        image_limit = params['image_limit']

    # Set the video limits if set in the params
    if 'video_limit' in params:
        video_limit = params['video_limit']

    # Set if audio should be processed
    if 'no_audio' in params:
        no_audio = params['no_audio']

    # Download the images
    game_resources['images'] = get_images(data[game_id], image_limit)

    # Download the videos
    game_resources['videos'] = get_videos(data[game_id], video_limit)

    # Generate the audio
    if not no_audio:
        game_resources['audio'] = get_audio(data[game_id])

    # Return the fetched data
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
