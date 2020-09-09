"""Most code was taken from Colin Raffle on
https://nbviewer.jupyter.org/github/craffel/midi-ground-truth/blob/master/Statistics.ipynb"""

import joblib

import pretty_midi

def compute_statistics(midi_file):
    """
        Given a path to a MIDI file, compute a dictionary of statistics about it

        Parameters
        ----------
        midi_file : str
            Path to a MIDI file.

        Returns
        -------
        statistics : dict
            Dictionary reporting the values for different events in the file.
    """
    # Some MIDI files will raise Exceptions on loading, if they are invalid.
    # We just skip those.
    try:
        pm = pretty_midi.PrettyMIDI(midi_file)
        # Extract information events from MIDI file
        return {
            'n_instruments': len(pm.instruments),
            'program_numbers': [i.program for i in pm.instruments],
            'key_numbers': [k.key_number for k in pm.key_signature_changes],
            'tempos': list(pm.get_tempo_changes()[1]),
            'time_signature_changes': pm.time_signature_changes,
            'end_time': pm.get_end_time(),
            'lyrics': [l.text for l in pm.lyrics]
        }
    # Silently ignore exceptions for a clean presentation (sorry Python!)
    except Exception as e:
        print(e)
