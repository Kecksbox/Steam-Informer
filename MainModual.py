import steamScrapper
import composer
import youtubeUploader
import debugger_utility as du

steam_params = dict(
    debugging=dict(
        no_video=1,
        no_image=0,
        image_cap=10,
        video_cap=10,
        audio_cap=10,
        no_audio=0,
        no_composing=0,
        no_upload=1,
        keep_audio=0,
        keep_composed_video=1
    )
)

# Get the game_id of the game which needs to be processed next
game_id = steamScrapper.next_game()

# Get the resources of the game
game_resources = steamScrapper.fetch(game_id, steam_params) # Dungons2 is 262280

# Clean all data which isn´t needed anymore
du.run_cleaner(steam_params, game_resources)

# If activated, compose a video out of the game resources
if not du.is_debugging_option_enabled(steam_params, "no_composing"):
    composed_video = composer.compose(game_resources, steam_params)

    # Clean all data which isn´t needed anymore
    du.run_cleaner(steam_params, composed_video)

    # If activated, upload the composed video to the youtube channel
    if not du.is_debugging_option_enabled(steam_params, "no_upload"):
        youtubeUploader.upload(composed_video, steam_params)
        steamScrapper.set_game_as_processed(game_id)
