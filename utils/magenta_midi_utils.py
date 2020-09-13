import time
from pathlib import Path
from typing import Union, Optional, List

from note_seq import NoteSequence, sequence_proto_to_pretty_midi


def save_midi(sequences: Union[NoteSequence, List[NoteSequence]],
              output_dir: Optional[str] = None,
              prefix: str = "sequence"):
    """
    Adapted from
    https://github.com/PacktPublishing/hands-on-music-generation-with-magenta/blob/magenta-v2.0.1/Chapter04/note_sequence_utils.py.
    Writes the sequences as MIDI files to the "output" directory, with the
    filename pattern "<prefix>_<index>_<date_time>" and "mid" as extension.
        :param sequences: a NoteSequence or list of NoteSequence to be saved
        :param output_dir: an optional subdirectory in the output directory
        :param prefix: an optional prefix for each file
    """
    output_dir = Path("output", output_dir) if output_dir else "output"
    Path.mkdir(output_dir, parents=True, exist_ok=True)
    if not isinstance(sequences, list):
        sequences = [sequences]
    for (index, sequence) in enumerate(sequences):
        date_and_time = time.strftime("%Y-%m-%d_%H%M%S")
        filename = f"{prefix}_{index:02}_{date_and_time}.mid"
        path = output_dir / filename

        # Have to write it by hand since magenta uses temporary files in
        # tmp folders where you might nove access to
        pm = sequence_proto_to_pretty_midi(sequence)
        pm.write(str(path.absolute()))

        print(f"Generated midi file: {path.absolute()}")
