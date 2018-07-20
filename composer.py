from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip

def compose(resources):

    currentDuration = 0

    for x in range(len(resources['videos'])):
        resources['videos'][x] = VideoFileClip(resources['videos'][x]).set_start(currentDuration)
        currentDuration += resources['videos'][x].duration
    for x in range(len(resources['images'])):
        tmp = resources['images'][x]
        resources['images'][x] = ImageClip(resources['images'][x], duration=5).set_start(currentDuration)
        resources['images'][x].filename = tmp
        currentDuration += resources['images'][x].duration
    resources['audio'] = AudioFileClip(resources['audio'])

    return CompositeVideoClip(resources['videos'] + resources['images']).set_audio(resources['audio'])