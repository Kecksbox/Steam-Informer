import gc
import os
from moviepy.editor import CompositeVideoClip, CompositeAudioClip, AudioFileClip
import tempfile
import time


#def keep_audio(composed_audio):
#    audio_path = os.path.join(tempfile.gettempdir(), time.strftime("%Y%m%d-%H%M%S"))+'.mp3'
#    #composed_audio.write_audiofile(audio_path)
#    print('[debugger_utility] >>> Cleaner: Audio file at {path} was spared.'.format(path=audio_path))


def is_debugging_option_enabled(params, option_name):
    return not params == None and "debugging" in params and option_name in params["debugging"] and params["debugging"][option_name] == 1

def clean_dict(input, params): # revisit
    if not is_debugging_option_enabled(params, "no_audio"):
        if is_debugging_option_enabled(params, "keep_audio"):
            for x in input["audio"][1]:
                os.remove(x)
            print('[debugger_utility] >>> Cleaner: Audio file at {path} was spared.'.format(path=input["audio"][0]))
        else:
            for x in input["audio"][1]+[input["audio"][0]]:
                os.remove(x)
    for x in input["images"] + input["videos"]:
            os.remove(x)
    print("successfully cleaned.")

def clean_composite_clip(input, params):
    audio = input.audio
    input.close()
    if not is_debugging_option_enabled(params, "no_audio"):
        audio.close()
    for x in input.clips:
        x.close()

    gc.collect()

    if not is_debugging_option_enabled(params, "no_audio"):
        if not is_debugging_option_enabled(params, "keep_audio"):
            os.remove(audio.filename)
        else:
            print('[debugger_utility] >>> Cleaner: Audio file at {path} was spared.'.format(path=audio.filename))
        for x in audio.clips:
            os.remove(x)
    for x in input.clips:
        os.remove(x.filename)

    print("successfully cleaned.")

def run_cleaner(params, input):
    if is_debugging_option_enabled(params, "no_composing") and type(input) is dict:
        clean_dict(input, params)
    elif is_debugging_option_enabled(params, "no_upload") and isinstance(input, CompositeVideoClip):
        clean_composite_clip(input, params)
