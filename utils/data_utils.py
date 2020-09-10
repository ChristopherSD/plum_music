"""
Utility functions to work with data in the data directory.
"""

import csv
import json
import logging
import tables
from multiprocessing import Manager, Process
from pathlib import Path

import pandas as pd

import config.config as cnfg
from utils.lakh_utils import get_msd_score_matches, get_matched_midi_md5
from utils.msd_utils import *

logger = logging.getLogger(__name__)


def get_all_artists_count():
    """
    Counts all unique artist names in the LMD matched dataset.
    :return: A Counter of for each unqiue artist name.
    """
    pass


def get_num_matched_songs():
    """
    Count the number of h5 files in lmd_matched_h5
    :return: The number of songs in the LMD data set that have a MSD match
    """
    constants = cnfg.get_constants_dict()
    h5_dir = Path(constants["LMD_MATCHED_H5_DIR"])
    return len(list(h5_dir.rglob('TR*.h5')))


def _make_csv_database(verbose=0):
    """
    Make a csv database table with meta information about all the available songs in the LMD matched dataset.
    :param verbose Whether to print execution information or not (default=0).
    :return: A Path object showing the location the csv file is stored
    """
    constants = cnfg.get_constants_dict()
    h5_dir = Path(constants["LMD_MATCHED_H5_DIR"])
    all_h5_files = list(h5_dir.rglob('TR*.h5'))
    logger.info(f"Retrieved list of {len(all_h5_files)} h5 files")

    metadata_csv = Path(constants["DATA_PATH"], "lmd_metadata.csv")
    logger.debug(f"Metadata csv filepath is: {str(metadata_csv)}")

    with metadata_csv.open('w') as f:
        writer = csv.writer(f)

        matches = get_msd_score_matches()
        fieldnames = [
            'msdID',
            'md5',
            'artist',
            'track',
            'album',
            'genre']
        writer.writerow(fieldnames)
        for h5_path in all_h5_files:
            h5 = tables.open_file(str(h5_path))

            msd_id = h5_path.stem
            row = [
                msd_id,
                get_matched_midi_md5(msd_id, msd_score_matches=matches),
                get_artist(h5),
                get_title(h5),
                get_album(h5),
                get_genre(h5)
            ]
            writer.writerow(row)

            h5.close()

            if verbose:
                print(f"Wrote row:\n\t{row}")

    logger.info(f"Created file {metadata_csv.name}")
    return metadata_csv


def make_top_lastfm_genre_json(verbose=0):
    """
    Make a json file with containing the top genre for each MSD ID,
    fetched from the last.FM API's track.getTopTags method.
    WARNING: This function uses the lmd_metadata.csv file created with _make_csv_database
    for faster computation. Make sure to have the file created, otherwise a FileNotFoundError is thrown.
    :param verbose Whether to print execution information or not (default=0).
    :return: A Path object showing the location the json file is stored
    """
    constants = cnfg.get_constants_dict()
    df = pd.read_csv(constants["LMD_METADATA_CSV_FILE"])

    ''' Multiprocessing solution does not work
    manager = Manager()
    genre_dict = manager.dict()
    job = [Process(target=_add_genre_dict_entry, args=(genre_dict, row[1])) for row in df.iterrows()]
    [p.start() for p in job]
    [p.join() for p in job]'''

    genre_dict = dict()
    for i, row in df.iterrows():
        if verbose:
            print(f'Fetching tops tags for:\n\t{row["artist"]} - {row["track"]}')

        # TODO
        '''handle
        raise JSONDecodeError("Expecting value", s, err.value) from None
        json.decoder.JSONDecodeError: Expecting value: line 1 column 1(char 0)'''
        genre = get_lastfm_top_genre_tags(artist=row["artist"], title=row["track"], ignore_not_found=True)
        if genre:
            genre_dict[row["msdID"]] = genre[0]
            if verbose:
                print(f'Added genre "{genre[0]}"')
        elif verbose:
            print(f'Could not find {row["artist"]} - {row["track"]} in last.FM API')

    genre_json_path = constants["LASTFM_GENRE_MSDID_MATCHED_JSON"]
    with genre_json_path.open('w') as f:
        json.dumps(genre_dict)

    return genre_json_path


def _add_genre_dict_entry(genre_dict: dict, row):
    """
    SIDE EFFECTS: Add an entry to the given genre dictionary.
    :param genre_dict:
    :param row:
    :return:
    """
    genre_dict[row["msdID"]] = get_lastfm_top_genre_tags(artist=row["artist"], title=row["track"])
