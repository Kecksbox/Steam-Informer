import http.client
import httplib2
import os
import random
import sys
import time
import tempfile
import logger
from debugger_utility import clean_composite_clip
import datetime

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import debugger_utility as du

module_name = 'youtubeUploader'  # Specifies the name of the module

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
http.client.IncompleteRead, http.client.ImproperConnectionState,
http.client.CannotSendRequest, http.client.CannotSendHeader,
http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = ""

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body=dict(
    snippet=dict(
      title=options.title,
      description=options.description,
      tags=tags,
      categoryId=options.category
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)


def resumable_upload(insert_request):
    """This method implements an exponential backoff strategy to resume a failed upload."""

    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logger.log("Uploading file...", module_name)
            status, response = insert_request.next_chunk()
            if 'id' in response:
                logger.log("Video id '%s' was successfully uploaded." % response['id'], module_name)
            else:
                exit("The upload failed with an unexpected response: %s" % response)
        except (HttpError):
            logger.log("", module_name)

    if error is not None:
      logger.log(error, module_name)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      logger.log("Sleeping %f seconds and then retrying..." % sleep_seconds, module_name)
      time.sleep(sleep_seconds)


def upload(video_clip, params=None):
    # Variables for the Video
    title = 'Test Title'
    description = 'Video description'
    category = '22'
    keywords = 'Video keywords, comma separated'
    privacy_status = VALID_PRIVACY_STATUSES[1]
    playlist = 'test'  # (MBE vielleicht auch zu mehreren playlists)
    publish_at = datetime.datetime.strptime('2018-07-28UTC23:25:00.+0200', '%Y-%m-%d%Z%H:%M:%S.%z')  # MBE KP WAS DAS FÜR EIN TYPE SEIN MUSS (YYYY-MM-DDThh:mm:ss.sZ)
    default_language = 'en'
    default_audio_language = 'en'

    # Set the title
    if hasattr(video_clip, 'title'):
        title = video_clip.title

    # Set the description
    if hasattr(video_clip, 'description'):
        description = video_clip.description

    # Set the category
    if hasattr(video_clip, 'category'):
        category = video_clip.category

    # Set the keywords
    if hasattr(video_clip, 'keywords'):
        keywords = video_clip.keywords

    # Set the privacy_status
    if hasattr(video_clip, 'privacy_status'):
        privacy_status = video_clip.privacy_status

    # Set the playlist
    if hasattr(video_clip, 'playlist'):
        playlist = video_clip.playlist

    # Set the publish_at
    if hasattr(video_clip, 'publish_at'):
        publish_at = video_clip.publish_at

    # Set the default_language
    if hasattr(video_clip, 'default_language'):
        default_language = video_clip.default_language

    # Set the default_audio_language
    if hasattr(video_clip, 'default_audio_language'):
        default_audio_language = video_clip.default_audio_language

    # Configure the file which should be uploaded
    argparser.add_argument("--file", help="Video file to upload", default=video_clip)

    # Configure the title of the video
    argparser.add_argument("--title", help="Video title", default=title)

    # Configure the description of the video
    argparser.add_argument("--description", help="Video description", default=description)

    # Configure the category of the video
    argparser.add_argument("--category", default=category, help="Numeric video category. " +
    "See https://developers.google.com/youtube/v3/docs/videoCategories/list")

    # Configure the keyword for the video
    argparser.add_argument("--keywords", help="Video keywords, comma separated", default=keywords)

    # Configure the privacy status of the video
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
                           default=privacy_status, help="Video privacy status.")

    # Configure the playlist the video should be saved in
    argparser.add_argument("--playlist", help="Playlist the video will be added to", default=playlist)

    # Configure the publishing date of the video
    argparser.add_argument("--publish-at", help="The date and time the video should be published", default=publish_at)

    # Configure the language of the video
    argparser.add_argument("--default-language", help="Language", default=default_language)

    # Configure the audio language of the video
    argparser.add_argument("--default-audio-language", help="Audio language", default=default_audio_language)

    # Combine the arguments to parse them
    args = argparser.parse_args()

    # Define a path be able to compile the video
    path = os.path.join(tempfile.gettempdir(), time.strftime("%Y%m%d-%H%M%S"))+'.mp4'

    # Write the video to upload it
    args.file.write_videofile(path, fps=30)

    # Add the location of the file to the args
    args.file = path

    # Give the video clip a filename property which is the path
    video_clip.filename = path

    # MBE WHAT IS THIS DOING?
    params["composed_video_allready_created"] = 1

    # Get a service reserved
    youtube = get_authenticated_service(args)

    try:
        # Begin to upload the video
        initialize_upload(youtube, args)
    except HttpError:
        logger.log("", module_name)
    finally:
        # MBE Clean the clips a composed video had
        if hasattr(video_clip, 'clips'):
            clean_composite_clip(video_clip, params)
