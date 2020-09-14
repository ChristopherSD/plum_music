import time
import tempfile
import os
from pathlib import Path
from typing import Union, Optional, List

from config.config import get_constants_dict
from utils.lakh_utils import *

import note_seq as ns
import pretty_midi
from note_seq import NoteSequence


def save_midi(sequences: Union[NoteSequence, List[NoteSequence]],
              output_dir: Optional[str] = None,
              output_names: Optional[List[str]] = None,
              overwrite=False,
              prefix: str = "sequence"):
    """
    Adapted from
    https://github.com/PacktPublishing/hands-on-music-generation-with-magenta/blob/magenta-v2.0.1/Chapter04/note_sequence_utils.py.
    Writes the sequences as MIDI files to the "output" directory, with the
    filename pattern "<prefix>_<index>_<date_time>" and "mid" as extension, if output_name is not given.
        :param overwrite:
        :param sequences: a NoteSequence or list of NoteSequence to be saved
        :param output_dir: an optional specified output directory
        :param output_names: an optional name for the file to be saved under, without extension. Has to be
        the same size as sequences.
        :param overwrite: If false (default), does not create a new MIDI file if the cleaned file already exists.
        Otherwise a new file is created that overwrites the existing one.
        :param prefix: an optional prefix for each file
    """
    if len(sequences) != len(output_names):
        raise ValueError("The list of output_names has to be same size as the list of sequences.")

    consts = get_constants_dict()

    output_dir = Path(output_dir) if output_dir else Path(consts["DATA_DIR"])
    Path.mkdir(output_dir, parents=True, exist_ok=True)
    if not isinstance(sequences, list):
        sequences = [sequences]
    for (index, sequence) in enumerate(sequences):
        date_and_time = time.strftime("%Y-%m-%d_%H%M%S")
        if output_names:
            filename = output_names[index] + ".mid"
        else:
            filename = f"{prefix}_{index:02}_{date_and_time}.mid"
        path = output_dir / filename

        if path.exists() and not overwrite:
            continue

        # Have to write it by hand since magenta uses temporary files in
        # tmp folders where you might not have access to
        pm = ns.sequence_proto_to_pretty_midi(sequence)
        pm.write(str(path.absolute()))

        print(f"Generated midi file: {path.absolute()}")


def load_midi(msd_id: str, remove_changes: bool = True) -> ns.NoteSequence:
    """
    Loads a midi file from the Lakh MIDI dataset given a MSD ID.
    If remove_changes is set to True (default) only the first tempo and key/time signature is kept.
    :param msd_id: An MSD ID matching a MIDI file in the Lakh MIDI dataset.
    :param remove_changes: If True (default), all tempo and key/time signature changes are removed and only the first
    instance of each is kept.
    :return: A NoteSequence of the MIDI file given by the MSD ID
    """
    consts = get_constants_dict()
    matches = get_msd_score_matches()
    md5 = get_matched_midi_md5(msd_id, matches)
    midi_path = get_midi_path(msd_id, md5)

    if remove_changes:
        # load to pretty midi first to remove tempo and key changes
        pm = pretty_midi.PrettyMIDI(str(midi_path))
        pm = _remove_tempo_and_key_changes(pm)

        tmp_file, tmp_filename = tempfile.mkstemp(suffix='.mid', dir=consts["DATA_PATH"])
        pm.write(tmp_filename)
        note_seq = ns.midi_file_to_note_sequence(tmp_filename)
        os.close(tmp_file)
        os.unlink(tmp_filename)
    else:
        note_seq = ns.midi_file_to_note_sequence(midi_path)

    return ns.sequences_lib.remove_redundant_data(note_seq)


def _remove_tempo_and_key_changes(midi: pretty_midi.PrettyMIDI) -> pretty_midi.PrettyMIDI:
    """
    Removes all tempo and key/time signature changes from the given PrettyMIDI.
    This is a simple approach, keeping only the first instance of each, discarding all the rest.
    :param midi: The PrettyMidi object on which to work on.
    :return: The PrettyMidi object with all tempo and key/time signature changes removed.
    """
    if midi._tick_scales:
        midi._tick_scales = [midi._tick_scales[0]]
    if midi.key_signature_changes:
        midi.key_signature_changes = [midi.key_signature_changes[0]]
    if midi.time_signature_changes:
        midi.time_signature_changes = [midi.time_signature_changes[0]]
    return midi
