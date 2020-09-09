"""
Utility functions to work with Million Song Dataset records stored in data/lmd_matched_h5.
All functions work on a given table.File to access the data and assume only one song per file.
"""
from typing import List

import tables


def get_title(h5: tables.File) -> str:
    return h5.root.metadata.songs.cols.title[0]


def get_artist(h5: tables.File) -> str:
    return h5.root.metadata.songs.cols.artist_name[0].decode()


def get_album(h5: tables.File) -> str:
    return h5.root.metadata.songs.cols.release[0].decode()


def get_artist_terms(h5: tables.File) -> List[str]:
    return [term.decode() for term in h5.root.metadata.artist_terms]
