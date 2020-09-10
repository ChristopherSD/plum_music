"""
Utility functions to work with data in the data directory.
"""

import csv
import logging
import tables
from pathlib import Path

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

    metadata_csv = Path(constants["DATA_PATH"],  "lmd_metadata.csv")
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
