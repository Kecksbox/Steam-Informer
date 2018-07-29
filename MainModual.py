import steamScrapper
import logger
import composer
import youtubeUploader
import debugger_utility as du
from moviepy.editor import VideoFileClip

steam_params = dict(  # MBE
    debugging=dict(
        # Params for steamScrapper
        image_limit=-1,  # Limits the amount of images downloaded (-1 no restriction)
        video_limit=-1,  # Limits the amount of videos downloaded (-1 no restriction)
        generate_audio=True,  # Activates(True) or deactivates(False) the generation of audio

        # Params for composer
        compose_video=True,  # Activates(True) or deactivates(False) the composing of the final video

        # Params for uploader
        upload_trailer=False,  # Activates(True) or deactivates(False) the upload of the trailers
        upload_composed_video=True,  # Activates(True) or deactivates(False) the upload of the final video

        # Old params MBE
        no_video=1,
        no_image=0,
        image_cap=10,
        video_cap=10,
        audio_cap=10,
        no_audio=0,
        no_composing=0,
        no_upload=0,
        keep_audio=0,
        keep_composed_video=1
    )
)

# A dict to toggle parts of the system on and off or restrict them
debugging = dict(
        # Params for steamScrapper
        image_limit=-1,  # Limits the amount of images downloaded (-1 no restriction)
        video_limit=-1,  # Limits the amount of videos downloaded (-1 no restriction)
        generate_audio=True,  # Activates(True) or deactivates(False) the generation of audio

        # Params for composer
        compose_video=True,  # Activates(True) or deactivates(False) the composing of the final video

        # Params for uploader
        upload_trailer=False,  # Activates(True) or deactivates(False) the upload of the trailers
        upload_composed_video=True,  # Activates(True) or deactivates(False) the upload of the final video
)

# To get the nltk 'Punkt' error out of the way, uncomment the two lines below ones
# import nltk
# nltk.download('punkt')

module_name = 'mainModule'

# Get the game_id of the game which needs to be processed next
game_id = steamScrapper.next_game()

# Log the that we start to work on a new game
logger.log('\n\nStart with the processing of the next game(' + game_id + ')', module_name)

# Get the resources of the game
game_resources = steamScrapper.fetch(262280, steam_params)  # Dungons2 is 262280

print(game_resources)

# Clean all data which isn´t needed anymore
du.run_cleaner(steam_params, game_resources)  # MBE

"""MBE WIR SOLLTEN UNS ÜBERLEGEN WIE WIR DAS BEARBEITEN WENN WIR EINEN TEIL DER TRAILER HOCHGELADEN HABEN
   UND DAS PROGRAM ABSTÜRTZT, SOMIT DAS GAME NICHT ALS BEENDET MARKIERT WIRD.
   EINE LÖSUNG WÄRE DAS WIR VOR EINEM UPLOAD IMMER EINMAL CHECKEN,
    OB DER NAME DES VIDEOS BEREITS AUF DEM CHANNEL EXISTIERT 
    
    Zudem ist es wichtig, das wir dafür sorgen, das auch exceptions im Log erscheinen.
    Gegebenenfalls über ein try catch im main modul
    
    Gegebenenfalls sollten wir drüber nachdenken die Limiter in eigene Funktion kabseln
    
    Wir müssen schauen, dass wir auch die englischen Videos herruntergeladen bekommen
    
    Welche Kategorie brauchen unsere videos? Siehe die 'category' in video file uploader
    
    Überleg mal eine Datenstruktur mit allen Informationen durch die Piepeline zu schicken,
    möglichwerweise sollte man dann über einen rewrite und eine gute Kapselung nachdenken
    
    Es stimmt etwas mit den Bildern nicht, sie scheinen gezoomt zu werden."""

# +++++ Handle the trailers +++++
if debugging['upload_trailer']:
    # Upload each trailer
    for video in game_resources['videos']:
        youtubeUploader.upload(VideoFileClip(video), steam_params)


# +++++ Handle the composed video +++++
if debugging['compose_video']:
    # Compose the final video
    composed_video = composer.compose(game_resources, steam_params)

    # Clean all data which isn´t needed anymore
    du.run_cleaner(steam_params, composed_video)

    # If activated, upload the composed video to the youtube channel
    if debugging['upload_composed_video']:
        youtubeUploader.upload(composed_video, steam_params)
        steamScrapper.set_game_as_processed(game_id)
