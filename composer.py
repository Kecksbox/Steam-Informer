from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip

import debugger_utility as du

def compose(resources, params):

    currentDuration = 0

    for x in range(len(resources['videos'])):
        resources['videos'][x] = VideoFileClip(resources['videos'][x]).set_start(currentDuration)
        currentDuration += resources['videos'][x].duration
    for x in range(len(resources['images'])):
        tmp = resources['images'][x]
        resources['images'][x] = ImageClip(resources['images'][x], duration=5).set_start(currentDuration)
        resources['images'][x].filename = tmp
        currentDuration += resources['images'][x].duration
    if not du.is_debugging_option_enabled(params, "no_audio"):
        resources['audio'] = AudioFileClip(resources['audio'])
        return CompositeVideoClip(resources['videos'] + resources['images']).set_audio(resources['audio'])
    return CompositeVideoClip(resources['videos'] + resources['images'])