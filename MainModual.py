import steamScrapper
import composer
import youtubeUploader
import debugger_utility as du

steam_params = dict(
    debugging = dict(
        no_video = 1,
        no_image = 0,
        image_cap = 10,
        video_cap = 10,
        audio_cap = 10,
        no_audio = 0,
        no_composing = 0,
        no_upload = 1,
        keep_audio = 0,
        keep_composed_video = 1
    )
)

game_id = steamScrapper.next_game()

print(game_id)

game_resources = steamScrapper.fetch(game_id, steam_params) # Dungons2 is 262280

du.run_cleaner(steam_params, game_resources)
if not du.is_debugging_option_enabled(steam_params, "no_composing"):
    composed_video = composer.compose(game_resources, steam_params)

    du.run_cleaner(steam_params, composed_video)
    if not du.is_debugging_option_enabled(steam_params, "no_upload"):
        youtubeUploader.upload(composed_video, steam_params)

