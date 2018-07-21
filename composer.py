from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip, AudioFileClip

import debugger_utility as du


def set_up_audio_clip(audio_rescource):
    tmp =  AudioFileClip(audio_rescource[0])
    tmp.clips = audio_rescource[1]
    return tmp


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

    if du.is_debugging_option_enabled(params, "no_audio"):
        return CompositeVideoClip(resources['videos'] + resources['images'])
    return CompositeVideoClip(resources['videos'] + resources['images']).set_audio(set_up_audio_clip(resources['audio']))