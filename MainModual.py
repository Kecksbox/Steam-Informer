import steamScrapper
import composer
import youtubeUploader

params = dict(
    debugging = dict(
        single_file_mode = 1
    )
)

game_resources = steamScrapper.fetch(262280, params)

#composed_video = composer.compose(game_resources)

#youtubeUploader.upload(composed_video)

