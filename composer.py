from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip, AudioFileClip


def set_up_audio_clip(audio_resource):
    """MBE MUSS NOCH VON MALTE GESCHRIEBEN WERDEN; WAS MACHT DAS DING??"""

    # Create an audio file of the audio resource
    tmp = AudioFileClip(audio_resource[0])

    # Give the audio clip a property with all audios used to create the final one
    tmp.clips = audio_resource[1]

    # Return the audio clip
    return tmp


def compose(resources, params):
    """Creates a video clip out of the videos and the images of the game as well as the audio from the description"""

    # Set up a variable to save the duration of the clip
    current_duration = 0

    # Set the limit parameters
    process_images = True
    process_videos = True
    process_audio = True

    # Set if the images should be processed
    if 'image_limit' in params:
        if params['image_limit'] == 0:
            process_images = False

    # Set if the videos should be processed
    if 'video_limit' in params:
        if params['video_limit'] == 0:
            process_videos = False

    # Set if audio should be processed
    if 'generate_audio' in params:
        process_audio = params['generate_audio']

    # Add the videos to the composed clip
    if process_videos:
        for video in range(len(resources['videos'])):
            # Set the start of each video
            resources['videos'][video] = VideoFileClip(resources['videos'][video]).set_start(current_duration)

            # Set the new duration of the clip
            current_duration += resources['videos'][video].duration

    # Add the images to the composed clip
    if process_images:
        for image in range(len(resources['images'])):
            # Get the images into a work variable
            tmp = resources['images'][image]

            # Create an image clip and set the start properly
            resources['images'][image] = ImageClip(resources['images'][image], duration=5).set_start(current_duration)

            # Set the name of the image clip
            resources['images'][image].filename = tmp

            # Set the new duration for the clip
            current_duration += resources['images'][image].duration

    # Add the audio to the video clip
    if process_audio:
        # Create the final clip with audio
        return CompositeVideoClip(resources['videos'] + resources['images']).set_audio(
            set_up_audio_clip(resources['audio']))

    # Create the final clip without audio
    return CompositeVideoClip(resources['videos'] + resources['images'])
