import steamScrapper
import composer
import youtubeUploader

import debugger_utility as du

params = dict(
    debugging = dict(
        no_video = 1,
        no_image = 0,
        image_cap = 1,
        video_cap = 1,
        audio_cap = 2,
        no_audio = 0,
        no_composing = 1,
        no_upload = 1,
        keep_audio = 0,
    )
)

game_resources = steamScrapper.fetch(262280, params)

du.run_cleaner(params, game_resources)
if not du.is_debugging_option_enabled(params, "no_composing"):
    composed_video = composer.compose(game_resources, params)

    du.run_cleaner(params, composed_video)
    if not du.is_debugging_option_enabled(params, "no_upload"):
        youtubeUploader.upload(composed_video, params)

