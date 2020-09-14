"""
Functionalities to prepare data for use with the MusicVAE.
"""

import logging
from pathlib import Path
from typing import Union, List

import config.config as cnf
from utils.lakh_utils import get_matched_midi_md5, get_msd_score_matches
from utils.magenta_midi_utils import *

from mido import MidiFile

logger = logging.getLogger()


def prepare_midi(msd_ids: Union[str, List[str]]) -> List[Path]:
    """
    Load the midi file from the Lakh MIDI dataset.
    Remove all events that define key or time signature changes and tempo changes.
    Split the midi file by tracks and create new MIDI files for each track
    Then save them as a new MIDI files in data/cleaned/<midi_md5>.
    :param msd_ids: The MSD ID of the midi file to prepare, or a list of IDs.
    :return: The path(s) to the directories with the newly created MIDI files.
    """

    consts = cnf.get_constants_dict()
    cleaned_file_path = Path(consts["CLEANED_DATA_PATH"])

    if not isinstance(msd_ids, list):
        msd_ids = [msd_ids]

    new_names = [
        get_matched_midi_md5(msd_id, msd_score_matches=get_msd_score_matches())
        for msd_id in msd_ids
    ]
    cleaned_names = [cleaned_file_path / new_name / (new_name + "_cleaned") for new_name in new_names]

    new_midis = []
    for msd_id in msd_ids:
        new_midi = load_midi(msd_id=msd_id, remove_changes=True)
        new_midis.append(new_midi)

    for path in cleaned_names:
        if not path.parent.exists():
            path.parent.mkdir(parents=True)

    save_midi(new_midis, cleaned_file_path, output_names=[str(name) for name in cleaned_names])

    for cleaned_midi in cleaned_names:
        _split_tracks(cleaned_midi.with_suffix(".mid"))

    return [name.parent for name in cleaned_names]


def _split_tracks(midi_path: Path) -> List[Path]:
    """
    Create new midi files for each track in the given path.
    :param midi_path: The file to the original MIDI path, without suffix.
    :return: A list of Paths of the newly created MIDI files.
    """
    consts = cnf.get_constants_dict()
    cleaned_file_path = Path(consts["CLEANED_DATA_PATH"])

    mid = MidiFile(midi_path)
    out_paths = []

    for i, track in enumerate(mid.tracks):
        logger.info(f"Track {i}: {track.name}")
        new_mid = MidiFile()
        new_mid.tracks.append(track)
        out_path = cleaned_file_path / midi_path.parent / f"track{i}_{track.name}.mid"
        new_mid.save(str(out_path))
        out_paths.append(out_path)

    return out_paths
