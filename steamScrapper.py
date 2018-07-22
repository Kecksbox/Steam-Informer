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

import debugger_utility as du


# Global variables
pbar = None
downloaded = 0

def cleanhtml(raw_html):
    return re.sub(re.compile("<+(?!.*emphasis)(?!.*break).*"), '', raw_html)

def generate_ssml_from_html(html):
    soup = BeautifulSoup(html)

    for x in soup.find_all("h1"):
        x.name = "emphasis"
        x["level"] = "strong"

    for x in soup.find_all("br"):
        x.name = "break"
        x["time"] = "200ms"

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    tokens = tokenizer.tokenize(' '.join(cleanhtml(soup.prettify()).split()))

    text_list = [['<speak><emphasis level="moderate">', 0]]
    for token in tokens:
        text_list[-1][1] += len(token)
        if text_list[-1][1] > 1000:
            text_list[-1][0] += '</emphasis></speak>'
            text_list.append(['<speak><emphasis level="moderate">', 0])
        text_list[-1][0] += token

    return text_list

def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None
        sleep(1)

def log_download_template(source, type="unknowen"):
    print("""
-------------------------------------------------------------------------------
[SteamScrapper] >>> Downloading ({type}) : {source}
-------------------------------------------------------------------------------""".format(source=source, type=type))

def fetch(game_id, args=None):

    if isinstance(game_id, int):
        game_id = str(game_id)

    url = 'http://store.steampowered.com/api/appdetails?appids=' + game_id


    params = dict(
        origin='Chicago,IL',
        destination='Los+Angeles,CA',
        waypoints='Joplin,MO|Oklahoma+City,OK',
        sensor='false'
    )

    game_resources = dict(
        images = [],
        videos = [],
        audio = [None, []]
    )

    data = requests.get(url=url, params=params).json()

    #****************************************
    #                Images
    # ****************************************
    if not du.is_debugging_option_enabled(args, "no_image"):
        for x in data[game_id]['data']['screenshots']:
            log_download_template(x['path_full'], 'Image')
            game_resources['images'].append(urllib.request.urlretrieve(x['path_full'], None, show_progress)[0])
            if ((not args == None) and "debugging" in args) and ("image_cap" in args["debugging"] and len(game_resources['images']) == args["debugging"]["image_cap"]): # this is copyed for videos. We might want to make this a function. [Malte]
                break

    # ****************************************
    #                Videos
    # ****************************************
    if not du.is_debugging_option_enabled(args, "no_video"):
        for x in data[game_id]['data']['movies']:
            log_download_template(x['webm']['max'], 'Video')
            game_resources['videos'].append(urllib.request.urlretrieve(x['webm']['max'], None, show_progress)[0])
            if ((not args == None) and "debugging" in args) and  ("video_cap" in args["debugging"] and len(game_resources['videos']) == args["debugging"]["video_cap"]):
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
                if ((not args == None) and "debugging" in args) and ("audio_cap" in args["debugging"] and len(game_resources['audio'][1]) == args["debugging"]["audio_cap"]):
                    break

    return game_resources