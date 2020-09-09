"""Utilities to work with Lakh MIDI dataset. Mostly taken from
https://nbviewer.jupyter.org/github/craffel/midi-dataset/blob/master/Tutorial.ipynb"""

from pathlib import Path

# Local path constants
DATA_PATH = Path(__file__).parent.parent.absolute() / 'data'
# Path to the file match_scores.json distributed with the LMD
MATCH_SCORE_FILE = DATA_PATH / 'LMD-match_scores.json'


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
