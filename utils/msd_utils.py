"""
Utility functions to work with Million Song Dataset records stored in data/lmd_matched_h5.
All functions work on a given table.File to access the data and assume only one song per file.
"""
import json
import logging
import requests
from pathlib import Path
from typing import List, Optional

import tables

logging.basicConfig(filename='/home/chris/DSR/plum_music/logs/plum_main.log',
                    format="%(levelname) %(asctime)\n\t%(message)",
                    datefmt='%Y-%m-%d %H:%M')
logger = logging.getLogger(__name__)


def get_title(h5: tables.File) -> str:
    return h5.root.metadata.songs.cols.title[0].decode()


def get_artist(h5: tables.File) -> str:
    return h5.root.metadata.songs.cols.artist_name[0].decode()


def get_album(h5: tables.File) -> str:
    return h5.root.metadata.songs.cols.release[0].decode()


def get_genre(h5: tables.File) -> str:
    return h5.root.metadata.songs.cols.genre[0].decode()


def get_artist_terms(h5: tables.File) -> List[str]:
    return [term.decode() for term in h5.root.metadata.artist_terms]


def get_lastfm_top_genre_tags(h5: tables.File = None, artist: str = None, title: str = None, ignore_not_found=False) -> \
Optional[list]:
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
      :return: the list of tags
    """
    if h5 is not None:
        title = get_title(h5)
        artist = get_artist(h5)

    try:
        tags = _make_lastfm_top_tags_request(artist, title)
    except FileNotFoundError as ex:
        if ignore_not_found:
            tags = []
        else:
            raise ex

    logger.info(f"Successfully retrieved tags for '{artist}' - '{title}'")

    return tags


def _make_lastfm_top_tags_request(artist: str, title: str) -> Optional[list]:
    with (Path(__file__).parent.parent.absolute() / 'config' / 'lastFM-api.json').open('r') as f:
        key = (json.load(f))['API key']

    request = (
        f"https://ws.audioscrobbler.com/2.0/"
        f"?method=track.gettoptags"
        f"&artist={artist}"
        f"&track={title}"
        f"&api_key={key}"
        f"&format=json"
    )
    logger.info(f'Sending last.FM API request: {request}')
    response = requests.get(request, timeout=10)
    logger.info(f"Got last.FM API response: {response}")
    try:
        json_response = response.json()
    except Exception:
        print("Response content is not valid JSON")
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
        raise

    tags = [tag["name"] for tag in json_response["toptags"]["tag"]]
    return [tag.lower().strip() for tag in tags if tag]
