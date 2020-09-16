import json
import logging
from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent.absolute()
DATA_PATH = PROJECT_PATH / 'data'
TEST_PATH = PROJECT_PATH / 'tests'
MODELS_PATH = PROJECT_PATH / "models"


def set_up():
    """
    Runs all functions necessary to set up the configuration files.
    """
    set_up_constants()
    set_up_dir_structure()


def set_up_constants():
    """
    Create the constants.json file according to your file system.
    """

    constants = {
        "DATA_PATH": str(DATA_PATH),
        "TEST_PATH": str(TEST_PATH),
        "MODELS_PATH": str(MODELS_PATH),

        "TEST_DATA_PATH": str(TEST_PATH / 'testdata'),
        "LOG_DIR": str(PROJECT_PATH / 'logs'),
        "MODELS_MUSICVAE_PATH": str(MODELS_PATH / "musicVAE"),

        "CHECKPOINT_MUSICVAE_CAT_MEL": "cat-mel_2bar_big",
        "CHECKPOINT_MUSICVAE_HIERDEC_TRIO": "hierdec-trio_16bar",
        "CHECKPOINT_MUSICVAE_HIERDEC_MEL": "hierdec-mel_16bar",
        "CHECKPOINT_MUSICVAE_CAT_DRUMS_HIKL": "cat-drums_2bar_small.hikl",
        "CHECKPOINT_MUSICVAE_MULTITRACK": "model_fb256.ckpt",
        "CHECKPOINT_MUSICVAE_MULTITRACK_CONDITIONED": "model_chords_fb64.ckpt",
        "NAME_MUSICVAE_MULTITRACK": "hier-multiperf_vel_1bar_med",
        "NAME_MUSICVAE_MULTITRACK_CONDITIONED": "hier-multiperf_vel_1bar_med_chords",

        "CLEANED_DATA_PATH": str(DATA_PATH / 'cleaned'),

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


def set_up_dir_structure():
    """
    Sets up the directory structure as referenced in the constants dict, by creating all directories that do not exist
    yet. Does not create files!
    """
    constants = get_constants_dict()
    for key, value in constants.items():
        if "PATH" in key or "DIR" in key:
            path = Path(constants[key])
            if not path.suffix and not path.exists():
                path.mkdir(parents=True)


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
