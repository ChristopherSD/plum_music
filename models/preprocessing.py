"""
Functionalities to prepare data for use with the MusicVAE.
"""

import copy
import logging
from pathlib import Path
from typing import Union, List

import config.config as cnf
from utils.lakh_utils import get_matched_midi_md5, get_msd_score_matches
from utils.magenta_midi_utils import *
from utils.magenta_note_seq_utils import get_sec_for_num_bars

import note_seq as ns
import pretty_midi
from magenta.models.music_vae import configs
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
        split_by_tracks(cleaned_midi.with_suffix(".mid"))

    return [name.parent for name in cleaned_names]


def split_by_tracks(midi_path: Path) -> List[Path]:
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


def split_sequence_by_num_bars(seq: NoteSequence, n_bars: int = 1) -> List[NoteSequence]:
    bar_duration = get_sec_for_num_bars(seq, n_bars)
    return ns.split_note_sequence(seq, bar_duration)


def split_by_instrument(seq: NoteSequence) -> List[NoteSequence]:
    """
    Splits a given NoteSequence into a List of NoteSequences with one instrument each.
    :param seq: The NoteSequence to split
    :return: A list of NoteSequences containing one instrument each.
    """
    pm = ns.midi_io.note_sequence_to_pretty_midi(seq)
    instruments = []
    for i in range(len(pm.instruments)):
        new_pm = copy.deepcopy(pm)
        new_pm.instruments = [pm.instruments[i]]
        instruments.append(new_pm)

    # ns.melody_inference.infer_melody_for_sequence()
    return [ns.midi_to_note_sequence(single_instrument) for single_instrument in instruments]


def extract_melodies(seqs: List[NoteSequence], model_name: str) -> List[NoteSequence]:
    """
    Adapted from:
    https://colab.research.google.com/github/magenta/magenta-demos/blob/master/colab-notebooks/MusicVAE.ipynb#scrollTo=C-WE4Nq2OJxH

    Extract melodies from MIDI files. This will extract all unique 16-bar melodies using a
    sliding window with a stride of 1 bar.
    Uses the data converter of the given model (which therefore should be a melody model).
    :param seqs: A list of note sequences.
    :param model_name: The name of the model whose data converter to use.
    :return: A list of sequences
    """
    model_config = configs.CONFIG_MAP[model_name]
    extracted_mels = []
    for seq in seqs:
        extracted_mels.extend(
            model_config.data_converter.from_tensors(
                model_config.data_converter.to_tensors(seq)[1]))

    return extracted_mels


def extract_multitracks(seq: NoteSequence) -> List[NoteSequence]:
    """
    Splits the given NoteSequence in sequences of maximum 8 tracks, as required by the Multiperformance Model.
    :param seq: The sequence to split up
    :return: A list of note sequences, each containing a maximum of 8 tracks.
    """
    n = 8
    pm = ns.midi_io.note_sequence_to_pretty_midi(seq)
    num_tracks = len(pm.instruments)
    tracks_instruments = [
        pm.instruments[i:i + n]
        for i in range(0, num_tracks, n)
    ]

    splitted = []
    for i in tracks_instruments:
        new_pm = copy.deepcopy(pm)
        new_pm.instruments = i
        splitted.append(new_pm)

    return [ns.midi_to_note_sequence(split) for split in splitted]
