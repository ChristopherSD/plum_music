import json
import logging
from pathlib import Path
from typing import Optional

import requests
import tables

from utils.msd_utils import get_title, get_artist
from config.config import set_up_logging_basic_config

set_up_logging_basic_config()
logger = logging.getLogger(__name__)


def get_lastfm_top_genre_tags(
        h5: tables.File = None,
        artist: str = None,
        title: str = None,
        ignore_not_found=False
) -> Optional[list]:
    """
      Adapted from
      https://github.com/PacktPublishing/hands-on-music-generation-with-magenta/blob/master/Chapter06/chapter_06_example_02.py

      Returns the top tags (ordered most popular first) from the Last.fm API
      using the title and the artist name from the h5 database, or the one provided.
      :param h5: The h5 database. If given, artist and title argument are ignored.
      :param artist: The name of the artist of the track to look up.
      If given, title argument must be given and h5 must be None.
      :param title: The title of the track to look up.
      If given, artist argument must be given and h5 must be None.
      :param ignore_not_found: If True, ignores errors from the last.FM API if the given track is not found and
      returns an empty list (default=False).
      :return: The list of tags, or an empty list if ignore_not_found is set to true and no tags where found.
    """
    if h5 is not None:
        title = get_title(h5)
        artist = get_artist(h5)

    try:
        tags = execute_lastfm_top_tags_request(artist, title)
    except FileNotFoundError as ex:
        if ignore_not_found:
            tags = []
        else:
            raise ex

    logger.info(f"Successfully retrieved tags for '{artist}' - '{title}'")

    return tags


def execute_lastfm_top_tags_request(artist: str, title: str) -> Optional[list]:
    """
    Creates and executes a GET request to the last.FM API with the method track.getTopTags.
    :param artist: The artist name of the song to get the tags for.
    :param title: The title of the song to get the tags for.
    :return: A list of tags
    """
    request = create_lastfm_top_tags_request(artist, title)

    logger.info(f'Sending last.FM API request: {request}')
    response = requests.get(request, timeout=10)
    logger.info(f"Got last.FM API response: {response}")
    try:
        json_response = response.json()
    except Exception as ex:
        logger.error("Response content is not valid JSON")
        raise ex

    logger.info(f"Extracted response JSON:\n{json_response}")

    if "error" in json_response:
        ex = FileNotFoundError(f"Error in request for '{artist}' - '{title}':"
                               f"'{json_response['message']}'")
        logger.error(ex)
        raise ex
    if "toptags" not in json_response:
        ex = Exception(f"Error in request for '{artist}' - '{title}':"
                       f"no top tags")
        logger.error(ex)
        raise ex

    tags = [tag["name"] for tag in json_response["toptags"]["tag"]]
    return [tag.lower().strip() for tag in tags if tag]


def create_lastfm_top_tags_request(artist: str, title: str) -> str:
    """
    Create the GET request string to the last.FM API with the method track.getTopTags.
    :param artist: The artist name of the song to get the tags for.
    :param title: The title of the song to get the tags for.
    :return: A string containing the request for the given song
    (not converted to correct form yet, may contain forbidden characters)
    """
    with (Path(__file__).parent.parent.absolute() / 'config' / 'lastFM-api.json').open('r') as f:
        key = (json.load(f))['API key']

    return (
        f"https://ws.audioscrobbler.com/2.0/"
        f"?method=track.gettoptags"
        f"&artist={artist}"
        f"&track={title}"
        f"&autocorrect=1"
        f"&api_key={key}"
        f"&format=json"
    )
