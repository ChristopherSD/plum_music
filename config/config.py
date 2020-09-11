import json
import logging
from pathlib import Path


def set_up():
    """
    Runs all functions necessary to set up the configuration files.
    """
    set_up_constants()


def set_up_constants():
    """
    Create the constants.json file according to your file system.
    """
    PROJECT_PATH = Path(__file__).parent.parent.absolute()
    DATA_PATH = PROJECT_PATH / 'data'
    TEST_PATH = PROJECT_PATH / 'tests'

    constants = {
        "DATA_PATH": str(DATA_PATH),
        "TEST_PATH": str(TEST_PATH),
        "TEST_DATA_PATH": str(TEST_PATH / 'testdata'),
        "LOG_DIR": str(PROJECT_PATH / 'logs'),
        "FULL_FILENAMES_PATH": str(DATA_PATH / 'LMD-full_filenames.json'),
        "MATCH_SCORE_FILE": str(DATA_PATH / 'LMD-match_scores.json'),
        "LASTFM_GENRE_MSDID_MATCHED_JSON": str(DATA_PATH / 'LASTFM_GENRE_MSDID_MATCHED.json'),
        "LMD_MATCHED_DIR": str(DATA_PATH / 'lmd_matched'),
        "LMD_MATCHED_H5_DIR": str(DATA_PATH / 'lmd_matched_h5'),
        "LMD_METADATA_CSV_FILE": str(DATA_PATH / 'lmd_metadata.csv'),
        "NUM_LMD_MATCHED_SONGS": 31034
    }

    with (Path(__file__).parent.absolute() / "constants.json").open('w') as f:
        return json.dump(constants, f)


def set_up_logging_basic_config():
    constants = get_constants_dict()
    logging.basicConfig(filename=str(Path(constants["LOG_DIR"], 'plum_main.log')),
                        format="%(name)s: %(levelname)s %(asctime)s\n\t%(messages)s",
                        datefmt='%Y-%m-%d %H:%M',
                        filemode='w')


def get_constants_dict() -> dict:
    """
    Reads the constants config file to return as a dict.
    :return: A dict of constant names (key) and their values.
    """
    with (Path(__file__).parent.absolute() / "constants.json").open('r') as f:
        return json.load(f)
