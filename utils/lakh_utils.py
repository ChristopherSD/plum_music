"""Utilities to work with Lakh MIDI dataset. Mostly taken from
https://nbviewer.jupyter.org/github/craffel/midi-dataset/blob/master/Tutorial.ipynb
and
https://github.com/PacktPublishing/hands-on-music-generation-with-magenta"""

import json
import logging
from pathlib import Path
from typing import Dict, Union, List

import config.config as cnfg

cnfg.set_up_logging_basic_config()
logger = logging.getLogger(__name__)

constants = cnfg.get_constants_dict()
# Local path constants
DATA_PATH = Path(constants["DATA_PATH"])
# Path to the file match_scores.json distributed with the LMD
MATCH_SCORE_FILE = Path(constants["MATCH_SCORE_FILE"])


# Utility functions for retrieving paths
def msd_id_to_dirs(msd_id: str) -> Path:
    """Given an MSD ID, generate the path prefix.
    E.g. TRABCD12345678 -> A/B/C/TRABCD12345678"""
    return Path(msd_id[2], msd_id[3], msd_id[4], msd_id)


def msd_id_to_h5(msd_id: str) -> Path:
    """Given an MSD ID, return the path to the corresponding h5"""
    return Path(DATA_PATH, 'lmd_matched_h5', msd_id_to_dirs(msd_id).with_suffix('.h5'))


def get_midi_path(msd_id: str, midi_md5: str):
    """Given an MSD ID and MIDI MD5, return path to a MIDI file."""
    return Path(DATA_PATH, 'lmd_matched', msd_id_to_dirs(msd_id), midi_md5 + '.mid')


def get_msd_score_matches(match_scores_path: Path = MATCH_SCORE_FILE) -> Dict:
    """
    Returns the dictionary of scores from the match scores file.

    :param match_scores_path: the match scores path
    :return: the dictionary of scores
    """
    with match_scores_path.open() as f:
        return json.load(f)


def get_matched_midi_md5(msd_id: str, msd_score_matches: dict, max_matched=True) -> Union[str, List[str]]:
    """
    Returns the MD5 of the MIDI with the highest match from its MSD id.
    :param msd_id: the MSD id
    :param msd_score_matches: the MSD score dict, use get_msd_score_matches
    :param max_matched: whether to only return the highest matched MIDI MD5 (default: true),
    or a list of all matched MIDI MD5s (false)
    :return: the matched MIDI MD5 if max_matched is True,
    else, a list of matched MIDI MD5s
    """
    matched_midi_md5 = None
    if max_matched:
        max_score = 0
        for midi_md5, score in msd_score_matches[msd_id].items():
            if score > max_score:
                max_score = score
                matched_midi_md5 = midi_md5
    else:
        matched_midi_md5 = msd_score_matches[msd_id].keys()

    if not matched_midi_md5:
        raise Exception(f"Not matched {msd_id}: {msd_score_matches[msd_id]}")
    return matched_midi_md5
