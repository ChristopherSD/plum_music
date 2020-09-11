"""
Utility functions to work with data in the data directory.
"""

import asyncio
import time

from aiohttp import ClientSession
import csv
import json
from pathlib import Path
from pprint import pprint

import pandas as pd

import config.config as cnfg
from utils.lakh_utils import get_msd_score_matches, get_matched_midi_md5
from utils.lastfm_utils import get_lastfm_top_genre_tags, create_lastfm_top_tags_request
from utils.msd_utils import *

cnfg.set_up_logging_basic_config()
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


def make_metadata_csv(verbose=0):
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

    with metadata_csv.open('w', encoding='utf-8') as f:
        start = time.time()
        writer = csv.writer(f)

        matches = get_msd_score_matches()
        fieldnames = [
            'msdID',
            'md5',
            'artist',
            'track',
            'album',
            'mb_genre',
            'mb_genre_count'
        ]
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
                get_musicbrainz_artist_tags(h5),
                get_musicbrainz_artist_tags_count(h5)
            ]
            writer.writerow(row)

            h5.close()

            if verbose:
                print(f"Wrote row:\n\t{row}")

    if verbose:
        print(f"Created file {metadata_csv.name} in {time.time() - start} seconds.")
    logger.info(f"Created file {metadata_csv.name} in {time.time() - start} seconds.")
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
            print(f'Fetching top tags for:\n\t{row["artist"]} - {row["track"]}')

        # TODO
        '''handle
        raise JSONDecodeError("Expecting value", s, err.value) from None
        json.decoder.JSONDecodeError: Expecting value: line 1 column 1(char 0)'''
        genre = []
        try:
            genre = get_lastfm_top_genre_tags(artist=row["artist"], title=row["track"], ignore_not_found=True)
        except Exception as ex:
            print(ex)

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


def make_top_lastfm_genre_json_parallel(verbose=0):
    """
    Make a json file with containing the top genre for each MSD ID,
    fetched from the last.FM API's track.getTopTags method.
    Uses asyncio and aiohttp to process requests asynchronously and speed up computation.
    Adapted from
    https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html.
    WARNING: This function uses the lmd_metadata.csv file created with _make_csv_database
    for faster computation. Make sure to have the file created, otherwise a FileNotFoundError is thrown.
    :param verbose Whether to print execution information or not (default=0).
    :return: A Path object showing the location the json file is stored
    """
    constants = cnfg.get_constants_dict()
    df = pd.read_csv(constants["LMD_METADATA_CSV_FILE"])

    lastfm_requests = []
    msd_ids = []
    for _, row in df.iterrows():
        lastfm_requests.append(create_lastfm_top_tags_request(artist=row["artist"], title=row["track"]))
        msd_ids.append(row["msdID"])

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(_get_genres(lastfm_requests))
    start = time.time()
    genres = loop.run_until_complete(future)
    stop = time.time()
    print(f"Took {stop - start} seconds to process {len(lastfm_requests)} requests in asynchronously.")
    pprint(genres[0:10])

    genre_json_path = constants["LASTFM_GENRE_MSDID_MATCHED_JSON"]
    genre_dict = {
        msd_id: genre
        for msd_id, genre in zip(msd_ids, genres)
    }
    with open(genre_json_path, 'w') as f:
        json.dump(genre_dict, f)

    return genre_json_path


async def _get_genres(lastfm_requests):
    """
    SIDE EFFECTS: Add an entry to the given genre dictionary.
    :param genre_dict:
    :return:
    """
    async with ClientSession() as session:
        tasks = []
        for req in lastfm_requests:
            tasks.append(
                asyncio.ensure_future(_fetch_genre(req, session=session))
            )

        genres = await asyncio.gather(*tasks)
        return genres
        '''tags = [
            {
                "name": tag["name"].lower.strip(),
                "count": tag["count"]
            }
            for track in genres
            for tag in track["toptags"]["tag"]
            if tag["name"]
        ]
        return tags'''


async def _fetch_genre(lastfm_request: str, session: ClientSession):
    try:
        async with session.get(lastfm_request) as response:
            return await response.json()
    except Exception as ex:
        print("Oh well, bollocks...", ex)
