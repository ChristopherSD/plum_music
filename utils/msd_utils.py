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


def get_lastfm_top_genre_tags(h5: tables.File) -> Optional[list]:
    """
      Adapted from
      https://github.com/PacktPublishing/hands-on-music-generation-with-magenta/blob/master/Chapter06/chapter_06_example_02.py

      Returns the top tags (ordered most popular first) from the Last.fm API
      using the title and the artist name from the h5 database.
      :param h5: the h5 database
      :return: the list of tags
    """
    title = get_title(h5)
    artist = get_artist(h5)
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
    json_response = response.json()
    logger.info(f"Extracted response JSON:\n{json_response}")

    if "error" in json_response:
        ex = Exception(f"Error in request for '{artist}' - '{title}':"
                       f"'{json_response['message']}'")
        logger.error(ex)
        raise ex
    if "toptags" not in json_response:
        ex = Exception(f"Error in request for '{artist}' - '{title}':"
                       f"no top tags")
        logger.error(ex)
        raise

    tags = [tag["name"] for tag in json_response["toptags"]["tag"]]
    tags = [tag.lower().strip() for tag in tags if tag]

    logger.info(f"Successfully retrieved tags for '{artist}' - '{title}'")

    return tags
