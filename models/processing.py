from pathlib import Path
from typing import List

import models.preprocessing as pre
from config.config import get_constants_dict
from utils.data_utils import get_all_songs_from_genre
from utils.magenta_models_utils import get_model

import numpy as np
import pandas as pd

import note_seq as ns
from magenta.models.music_vae.trained_model import NoExtractedExamplesError, MultipleExtractedExamplesError


def get_latent_encoding_for_genre(genre: str, model_name: str) -> List[np.ndarray]:
    """
    Encodes all MIDI files of the given genre into the chosen model's latent space. Skips all errors.
    :param genre:
    :param model_name:
    :return:
    """
    constants = get_constants_dict()
    all_files = get_all_songs_from_genre(genre)
    model = get_model(model_name)

    encodings = []
    num_successful, num_no_extracted, num_multiple_extracted, num_unsuccessful = 0, 0, 0, 0
    for song_id, song_path in all_files:
        try:
            z, _, _ = model.encode([ns.midi_file_to_note_sequence(str(song_path))])
        except NoExtractedExamplesError as ex:
            num_no_extracted += 1
            continue
        except MultipleExtractedExamplesError as ex:
            num_multiple_extracted += 1
            continue
        except Exception as ex:
            num_unsuccessful += 1
            continue
        else:
            encodings.append(z)
            num_successful += 1

    print(
        f"Extracted {num_successful} encodings from a total of {len(all_files)} files",
        f"Skipped {num_no_extracted + num_multiple_extracted + num_unsuccessful} files"
        f"Distribution:\n"
        f"\tNo Extracted Examples:{num_no_extracted}"
        f"\tMultiple Extracted Examples:{num_multiple_extracted}"
        f"\tOther exceptions:{num_unsuccessful}"
    )

    return encodings


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
                    not

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
