import note_seq as ns


def create_empty_note_sequence() -> ns.NoteSequence:
    note_sequence = ns.protobuf.music_pb2.NoteSequence()
    note_sequence.tempos.add().qpm = 120.0
    note_sequence.ticks_per_quarter = ns.constants.STANDARD_PPQ
    note_sequence.total_time = 0.0
    return note_sequence


def create_empty_note_seq_from_note_seq(old_note_seq: ns.NoteSequence) -> ns.NoteSequence:
    note_sequence = ns.protobuf.music_pb2.NoteSequence()
    note_sequence.tempos.add().qpm = old_note_seq.tempos[0].qpm
    note_sequence.ticks_per_quarter = old_note_seq.ticks_per_quarter
    note_sequence.total_time = 0.0
    return note_sequence


def get_sec_for_num_bars(note_seq: ns.NoteSequence, n_bars=2) -> float:
    """
    Calculates the duration of the given number of bars in the given NoteSequence in seconds.
    :param note_seq: The sequence from which to calculate the time from. Assumes there is only one tempo in the
    sequence, and the time signature's denominator is 4 (= quarters).
    :param n_bars: The number of bars for which to calculate the duration for.
    :return: The duration of the given number of bars of the sequence in seconds.
    """

    '''
    This is adapted from google Magenta Hierarchical DataConverter
    https://github.com/magenta/magenta/blob/81514d0107362f00825d0a0e36a1314e34c314ad/magenta/models/music_vae/data_hierarchical.py
    '''
    steps_per_quarter = 24
    quarters_per_bar = 4
    steps_per_bar = steps_per_quarter * quarters_per_bar

    if note_seq.tempos:
        quarters_per_minute = note_seq.tempos[0].qpm
    else:
        quarters_per_minute = note_seq.DEFAULT_QUARTERS_PER_MINUTE

    quarters_per_bar = steps_per_bar / steps_per_quarter
    hop_size_quarters = quarters_per_bar * n_bars
    hop_size_seconds = 60.0 * hop_size_quarters / quarters_per_minute

    return hop_size_seconds
