import requests
import urllib
import progressbar
import re
from bs4 import BeautifulSoup
from time import sleep
from tts import generateAudio

import debugger_utility as du


# Global variables
pbar = None
downloaded = 0

def cleanhtml(raw_html):
  cleanr = re.compile("<+(?!.*emphasis)(?!.*break).*")
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def generate_ssml_from_html(html):
    soup = BeautifulSoup(html)

    for x in soup.find_all("h1"):
        x.name = "emphasis"
        x["level"] = "strong"

    for x in soup.find_all("br"):
        x.name = "break"
        x["time"] = "200ms"

    return '<speak><emphasis level="moderate">' + ' '.join(cleanhtml(soup.prettify()).split()) + '</emphasis></speak>'

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
        audio = None
    )

    data = requests.get(url=url, params=params).json()

    #****************************************
    #                Images
    # ****************************************
    if not du.is_debugging_option_enabled(args, "no_image"):
        for x in data[game_id]['data']['screenshots']:
            log_download_template(x['path_full'], 'Image')
            game_resources['images'].append(urllib.request.urlretrieve(x['path_full'], None, show_progress)[0])
            if ((not args == None) and "debugging" in args) and (("single_image" in args["debugging"] and args["debugging"]["single_image"] == 1) or ("image_cap" in args["debugging"] and data[game_id]['data']['screenshots'].index(x) == args["debugging"]["image_cap"]-1)): # this is copyed for videos. We might want to make this a function. [Malte]
                break

    # ****************************************
    #                Videos
    # ****************************************
    if not du.is_debugging_option_enabled(args, "no_video"):
        for x in data[game_id]['data']['movies']:
            log_download_template(x['webm']['max'], 'Video')
            game_resources['videos'].append(urllib.request.urlretrieve(x['webm']['max'], None, show_progress)[0])
            if ((not args == None) and "debugging" in args) and (("single_video" in args["debugging"] and args["debugging"]["single_video"] == 1) or ("video_cap" in args["debugging"] and data[game_id]['data']['movies'].index(x) == args["debugging"]["video_cap"]-1)):
                break

    # ****************************************
    #                Audio
    # ****************************************
    if not du.is_debugging_option_enabled(args, "no_audio"):
        game_resources['audio'] = generateAudio(generate_ssml_from_html(data[game_id]['data']['detailed_description']))

    return game_resources