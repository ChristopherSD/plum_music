"""
Utility functions to work with Million Song Dataset records stored in data/lmd_matched_h5.
All functions work on a given table.File to access the data and assume only one song per file.
"""
import logging
from typing import List

import tables

from config.config import set_up_logging_basic_config

set_up_logging_basic_config()
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


def get_musicbrainz_artist_tags(h5: tables.File) -> str:
    return h5.root.musicbrainz.artist_mbtags[0].decode()


def get_musicbrainz_artist_tags_count(h5: tables.File) -> int:
    return int(h5.root.musicbrainz.artist_mbtags_count[0])
