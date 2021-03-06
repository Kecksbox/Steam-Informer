import gc
import os
import tempfile
import time
import logger
from moviepy.editor import CompositeVideoClip

module_name = 'debugger_utility'  # Specifies the name of the module


def is_debugging_option_enabled(params, option_name):
    return not params == None and "debugging" in params and option_name in params["debugging"] and params["debugging"][option_name] == 1


def cleaner_status(path, is_deleted):
    global module_name
    logger.log('{status} {path}'.format(status=('+' if (is_deleted == 0) else '-'), path=path), module_name)


def clean_dict(input, params):
    global module_name
    logger.log("""-------------------------------------------------------------------------------
[debugger_utility] >>> Cleaner started          (+: kept -: removed)
-------------------------------------------------------------------------------""", module_name, True)
    if not is_debugging_option_enabled(params, "no_audio"):
        for x in input["audio"][1]:
            os.remove(x)
            cleaner_status(x, 1)
        if not is_debugging_option_enabled(params, "keep_audio"):
            os.remove(input["audio"][0])
            cleaner_status(input["audio"][0], 1)
        else:
            cleaner_status(input["audio"][0], 0)
    for x in input["images"] + input["videos"]:
            os.remove(x)
            cleaner_status(x, 1)
    logger.log("""-------------------------------------------------------------------------------
[debugger_utility] >>> Successfully cleaned
-------------------------------------------------------------------------------""", module_name, True)


def clean_composite_clip(input, params):

    tmp = 0
    if is_debugging_option_enabled(params, "keep_composed_video") and ("composed_video_allready_created" not in params or params["composed_video_allready_created"] == 0):
        tmp = os.path.join(tempfile.gettempdir(), time.strftime("%Y%m%d-%H%M%S")) + '.mp4'
        input.write_videofile(tmp, fps=30)
    elif not is_debugging_option_enabled(params, "no_upload"):
        tmp = input.filename

    logger.log("""-------------------------------------------------------------------------------
[debugger_utility] >>> Cleaner started          (+: kept -: removed)
-------------------------------------------------------------------------------""", module_name, True)
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
            cleaner_status(audio.filename, 1)
        else:
            cleaner_status(audio.filename, 0)
        for x in audio.clips:
            os.remove(x)
            cleaner_status(x, 1)
    for x in input.clips:
        os.remove(x.filename)
        cleaner_status(x.filename, 1)

    if is_debugging_option_enabled(params, "keep_composed_video"):
        cleaner_status(tmp, 0)
    elif not tmp == 0:
        os.remove(tmp)
        cleaner_status(tmp, 1)
    logger.log("""-------------------------------------------------------------------------------
[debugger_utility] >>> Successfully cleaned
-------------------------------------------------------------------------------""", module_name, True)


def run_cleaner(params, input):
    if is_debugging_option_enabled(params, "no_composing") and type(input) is dict:
        clean_dict(input, params)
    elif is_debugging_option_enabled(params, "no_upload") and isinstance(input, CompositeVideoClip):
        clean_composite_clip(input, params)
