import pickle
import time
from pathlib import Path
from typing import List

import models.preprocessing as pre
from config.config import get_constants_dict
from utils.data_utils import get_all_songs_from_genre, get_all_songs_from_genres_of_size, get_metadata_dataframe
from utils.magenta_models_utils import get_model
from utils.lakh_utils import get_midi_path

import numpy as np
import pandas as pd

import note_seq as ns
from magenta.models.music_vae.trained_model import NoExtractedExamplesError, MultipleExtractedExamplesError


def get_encoding_for_genre(genre: str, model_name: str):
    """
    Encodes all MIDI files of the given genre into the chosen model's latent space. Skips all errors.
    :param genre:
    :param model_name:
    :return:
    """
    constants = get_constants_dict()
    all_files = get_all_songs_from_genre(genre)
    model = get_model(model_name)
    genres, encodings, msd_ids = [], [], []

    num_successful, num_no_extracted, num_multiple_extracted, num_unsuccessful = 0, 0, 0, 0
    no_extract, multi_extract, unsuccessful = [], [], []
    exceptions = []
    num_files = len(all_files)
    loop_count = 0

    for song_id, song_path in all_files:
        start = time.time()
        loop_count += 1
        try:
            seq = ns.midi_file_to_note_sequence(str(song_path))
        except Exception as ex:
            num_unsuccessful += 1
            exceptions.append(ex)
            continue
        else:
            try:
                z, _, _ = model.encode([seq])
            except NoExtractedExamplesError as ex:
                num_no_extracted += 1
                no_extract.append(song_id)
                continue
            except MultipleExtractedExamplesError as ex:
                num_multiple_extracted += 1
                multi_extract.append(song_id)
                continue
            except Exception as ex:
                num_unsuccessful += 1
                unsuccessful.append(song_id)
                exceptions.append(ex)
                continue
            else:
                encodings.append(z)
                genres.append(genre)
                msd_ids.append(song_id)
                num_successful += 1

        print(f"Processed one song in {time.time() - start} seconds")
        if loop_count % 20 == 0:
            print(
                f"In loop {loop_count}:\n"
                f"Currently processing genre {genre} with {num_files} songs\n"
                f"\tExtracted {num_successful} encodings from a {loop_count} processed files\n",
                f"\tSkipped {num_no_extracted + num_multiple_extracted + num_unsuccessful} files\n"
                f"Distribution:\n"
                f"\tNo Extracted Examples:{num_no_extracted}"
                f"\tMultiple Extracted Examples:{num_multiple_extracted}"
                f"\tOther exceptions:{num_unsuccessful}"
            )

    genres_file = Path(constants["DATA_PATH"]) / "encodings" / "genres_whole_song.pkl"
    encodings_file = Path(constants["DATA_PATH"]) / "encodings" / "encodings_whole_song.pkl"
    msd_ids_file = Path(constants["DATA_PATH"]) / "encodings" / "msd_ids_whole_song.pkl"

    with genres_file.open('wb') as g:
        pickle.dump(genres_file, g)
    with encodings_file.open('wb') as e:
        pickle.dump(genres_file, e)
    with msd_ids_file.open('wb') as m:
        pickle.dump(genres_file, m)

    print(exceptions)

    num_fails = num_no_extracted + num_multiple_extracted + num_unsuccessful
    print(
        f"Extracted {num_successful} encodings from a total of {num_files} files",
        f"Skipped {num_fails} files"
        f"Distribution:\n"
        f"\tNo Extracted Examples:{num_no_extracted}"
        f"\tMultiple Extracted Examples:{num_multiple_extracted}"
        f"\tOther exceptions:{num_unsuccessful}"
    )

    return genres, encodings, msd_ids


def get_latent_encoding_for_genre_split(genre: str, model_name: str, n_bars: int = 1) -> List[np.ndarray]:
    """
    Encodes all MIDI files of the given genre, split into n_bars,  into the chosen model's latent space. Skips all errors.
    :param genre:
    :param model_name:
    :param n_bars:
    :return:
    """
    constants = get_constants_dict()
    all_files = get_all_songs_from_genre(genre)
    model = get_model(model_name)

    encodings = []
    num_successful, num_no_extracted, num_multiple_extracted, num_unsuccessful = 0, 0, 0, 0
    exceptions = []
    for song_id, song_path in all_files:
        try:
            seq = ns.midi_file_to_note_sequence(str(song_path))
            splits = pre.split_sequence_by_num_bars(seq)
        except Exception as ex:
            num_unsuccessful += 1
            exceptions.append(ex)
            continue
        else:
            for split in splits:
                try:
                    z, _, _ = model.encode([split])
                except NoExtractedExamplesError as ex:
                    num_no_extracted += 1
                    continue
                except MultipleExtractedExamplesError as ex:
                    num_multiple_extracted += 1
                    continue
                except Exception as ex:
                    num_unsuccessful += 1
                    exceptions.append(ex)
                    continue
                else:
                    encodings.append(z)
                    num_successful += 1

    print(exceptions)

    print(
        f"Extracted {num_successful} encodings from a total of {len(all_files)} files",
        f"Skipped {num_no_extracted + num_multiple_extracted + num_unsuccessful} files"
        f"Distribution:\n"
        f"\tNo Extracted Examples:{num_no_extracted}"
        f"\tMultiple Extracted Examples:{num_multiple_extracted}"
        f"\tOther exceptions:{num_unsuccessful}"
    )

    return encodings


def get_encodings_for_genres_split(model_name: str):
    genre_files = get_all_songs_from_genres_of_size()
    model = get_model(model_name)
    genres, encodings, msd_ids = [], [], []

    num_successful, num_no_extracted, num_multiple_extracted, num_unsuccessful = 0, 0, 0, 0
    no_extract, multi_extract, unsuccessful = {}, {}, {}
    exceptions = []
    for genre, files in genre_files.items():
        for song_id, song_path in files:
            try:
                seq = ns.midi_file_to_note_sequence(str(song_path))
                splits = pre.split_sequence_by_num_bars(seq)
            except Exception as ex:
                num_unsuccessful += 1
                exceptions.append(ex)
                continue
            else:
                for split in splits:
                    try:
                        z, _, _ = model.encode([split])
                    except NoExtractedExamplesError as ex:
                        num_no_extracted += 1
                        no_extract[genre] = song_id
                        continue
                    except MultipleExtractedExamplesError as ex:
                        num_multiple_extracted += 1
                        multi_extract[genre] = song_id
                        continue
                    except Exception as ex:
                        num_unsuccessful += 1
                        unsuccessful[genre] = song_id
                        exceptions.append(ex)
                        continue
                    else:
                        encodings.append(z)
                        genres.append(genre)
                        msd_ids.append(song_id)
                        num_successful += 1

    print(exceptions)

    num_fails = num_no_extracted + num_multiple_extracted + num_unsuccessful
    num_files = sum(sum([v for v in genre_files.values()]))
    print(
        f"Extracted {num_successful} encodings from a total of {num_files} files",
        f"Skipped {num_fails} files"
        f"Distribution:\n"
        f"\tNo Extracted Examples:{num_no_extracted}"
        f"\tMultiple Extracted Examples:{num_multiple_extracted}"
        f"\tOther exceptions:{num_unsuccessful}"
    )

    return genres, encodings, msd_ids


def get_encodings_for_genres(model_name: str):
    genre_files = get_all_songs_from_genres_of_size()
    num_files_per_genre = {k: len(v) for k, v in genre_files.items()}
    model = get_model(model_name)
    genres, encodings, msd_ids = [], [], []

    num_successful, num_no_extracted, num_multiple_extracted, num_unsuccessful = 0, 0, 0, 0
    no_extract, multi_extract, unsuccessful = {}, {}, {}
    exceptions = []
    loop_count = 0
    print(
        f"Found {len(genre_files.keys())} genres that have more than 90 associated MIDI files\n"
        f"\tTotal number of files: {sum(num_files_per_genre.values())}"
        f"\t{num_files_per_genre}"
    )
    for genre, files in genre_files.items():
        print(f"Processing '{genre}' with {num_files_per_genre[genre]} files")
        for song_id, song_path in files:
            start = time.time()
            loop_count += 1
            try:
                seq = ns.midi_file_to_note_sequence(str(song_path))
            except Exception as ex:
                num_unsuccessful += 1
                exceptions.append(ex)
                continue
            else:
                try:
                    z, _, _ = model.encode([seq])
                except NoExtractedExamplesError as ex:
                    num_no_extracted += 1
                    no_extract[genre] = song_id
                    continue
                except MultipleExtractedExamplesError as ex:
                    num_multiple_extracted += 1
                    multi_extract[genre] = song_id
                    continue
                except Exception as ex:
                    num_unsuccessful += 1
                    unsuccessful[genre] = song_id
                    exceptions.append(ex)
                    continue
                else:
                    encodings.append(z)
                    genres.append(genre)
                    msd_ids.append(song_id)
                    num_successful += 1

            print(f"Processed one song in {time.time() - start} seconds")
            if loop_count % 20 == 0:
                print(
                    f"In loop {loop_count}:\n"
                    f"Currently processing genre {genre} with {len(genre_files[genre])} songs\n"
                    f"\tExtracted {num_successful} encodings from a {loop_count} processed files\n",
                    f"\tSkipped {num_no_extracted + num_multiple_extracted + num_unsuccessful} files\n"
                    f"Distribution:\n"
                    f"\tNo Extracted Examples:{num_no_extracted}"
                    f"\tMultiple Extracted Examples:{num_multiple_extracted}"
                    f"\tOther exceptions:{num_unsuccessful}"
                )

    constants = get_constants_dict()
    genres_file = Path(constants["DATA_PATH"]) / "encodings" / "genres_whole_song.pkl"
    encodings_file = Path(constants["DATA_PATH"]) / "encodings" / "encodings_whole_song.pkl"
    msd_ids_file = Path(constants["DATA_PATH"]) / "encodings" / "msd_ids_whole_song.pkl"

    with genres_file.open('wb') as g:
        pickle.dump(genres, g)
    with encodings_file.open('wb') as e:
        pickle.dump(encodings, e)
    with msd_ids_file.open('wb') as m:
        pickle.dump(msd_ids, m)

    print(exceptions)

    num_fails = num_no_extracted + num_multiple_extracted + num_unsuccessful
    num_files = sum([v for v in num_files_per_genre.values()])
    print(
        f"Extracted {num_successful} encodings from a total of {num_files} files",
        f"Skipped {num_fails} files"
        f"Distribution:\n"
        f"\tNo Extracted Examples:{num_no_extracted}"
        f"\tMultiple Extracted Examples:{num_multiple_extracted}"
        f"\tOther exceptions:{num_unsuccessful}"
    )

    return genres, encodings, msd_ids


def get_all_tracks_for_multitrack():
    meta = get_metadata_dataframe()

    valid_tracks = {}
    num_processed = 0
    for msd_id, md5 in zip(meta.msdID, meta.md5):
        try:
            seq = ns.midi_file_to_note_sequence(
                get_midi_path(msd_id, md5)
            )
        except Exception as e:
            pass
        else:
            if _is_multitrack_valid(seq):
                valid_tracks[msd_id] = md5
                print(f"Found a valid!!!!\n\tMSD ID: {msd_id}")

        num_processed += 1
        if num_processed % 50 == 0:
            print(f"Processed {num_processed} out of {len(meta.index)} files")

    return valid_tracks


def _is_multitrack_valid(seq: ns.NoteSequence) -> bool:
    """
    Check whether the given note sequence is valid for the multitrack model as described in google's paper:
    https://arxiv.org/pdf/1806.00195.pdf
    :param seq: The note sequence to check
    :return: True, if it is a valid sequence, false otherwise
    """
    # only one time signature in 4/4
    if (seq.time_signatures and len(seq.time_signatures) == 1) \
            and not \
            (seq.time_signatures[0].numerator == 4 and seq.time_signatures[0].denominator == 4):
        return False

    # number of tracks min 2 and max 8
    pm = ns.sequence_proto_to_pretty_midi(seq)
    if pm.instruments and not (2 <= len(pm.instruments) <= 8):
        return False

    # max 64 events per track
    for inst in pm.instruments:
        num_events = 0
        if inst.notes:
            num_events += len(inst.notes)
        if inst.pitch_bends:
            num_events += len(inst.pitch_bends)
        if inst.control_changes:
            num_events += len(inst.control_changes)

        if num_events > 64:
            return False

    return True
