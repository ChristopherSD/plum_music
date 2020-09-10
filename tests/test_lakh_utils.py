import json
import unittest
from pathlib import Path
from random import randint

from utils.lakh_utils import *

DATA_PATH = Path(__file__).parent.parent.absolute() / 'data'
FULL_FILENAMES_PATH =  DATA_PATH / 'LMD-full_filenames.json'
MATCH_SCORE_FILE = DATA_PATH / 'LMD-match_scores.json'


class TestLakhUtils(unittest.TestCase):

    def test_msd_id_to_dirs(self):
        """
        Test that an MSD ID is split into a correct file path
        by checking whether the filepath exists in the data  matched directory.
        """
        with MATCH_SCORE_FILE.open('r') as f:
            match_data_items = list(json.load(f).items())
            test_entry = match_data_items[randint(0, len(match_data_items) - 1)]

        msd_id = test_entry[0]
        msd_id_path = msd_id_to_dirs(msd_id)
        full_path = DATA_PATH / 'lmd_matched' / msd_id_path
        self.assertTrue(full_path.exists(), msg=f"MSD ID path {full_path} does not exist")
