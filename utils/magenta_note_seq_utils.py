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

    # quarter per minutes divided by 60 seconds (a minute)
    quarter_per_second = note_seq.tempos[0].qpm / 60
    # duration of one bar
    # bar = note_seq.time_signatures[0].numerator * quarter_per_second
    bar = 4 * quarter_per_second
    # duration of the given number of bars
    return bar * n_bars
