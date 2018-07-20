import gc
import os
from moviepy.editor import CompositeVideoClip

def convert_to_list(elem):
    return  [] if (elem == None) else [elem]

def is_debugging_option_enabled(params, option_name):
    return not params == None and "debugging" in params and option_name in params["debugging"] and params["debugging"][option_name] == 1

def run_cleaner(params, input):
    if is_debugging_option_enabled(params, "no_composing") and type(input) is dict:
        for x in input["images"] + input["videos"] + convert_to_list(input["audio"]):
            os.remove(x)
        print("successfully cleaned.")
    else:
        if is_debugging_option_enabled(params, "no_upload") and isinstance(input, CompositeVideoClip):
            input.close()
            if not is_debugging_option_enabled(params, "no_audio"):
                input.audio.close()
            for x in input.clips:
                x.close()

            gc.collect()

            if not is_debugging_option_enabled(params, "no_audio"):
                os.remove(input.audio.filename)
            for x in input.clips:
                os.remove(x.filename)

            print("successfully cleaned.")