import json
import unittest
import tables
from pathlib import Path
from random import randint

from utils.msd_utils import *

DATA_PATH = Path(__file__).parent.parent.absolute() / 'data'
TEST_DATA_PATH = Path(__file__).parent.absolute() / 'testdata'
FULL_FILENAMES_PATH = DATA_PATH / 'LMD-full_filenames.json'
MATCH_SCORE_FILE = DATA_PATH / 'LMD-match_scores.json'

with MATCH_SCORE_FILE.open('r') as f:
    match_data_items = json.load(f)


class TestMSDUtils(unittest.TestCase):

    def test_get_lastfm_top_genre_tags(self):
        """
        Test that correct tags are returned for valid request and
        exceptions are raised for invalid ones.
        """

        # Test valid request with Artist 'Cyndi Lauper' adn Title 'Into The Nightlife'
        tags = get_lastfm_top_genre_tags(tables.open_file(TEST_DATA_PATH / "TRAAAGR128F425B14B.h5"))
        result_tags = ['dance', 'pop', 'electronic', 'female vocalists', '2008', 'catchy', 'female vocalist',
                       'cyndi lauper', 'energetic', '00s', 'electronica', 'female', 'sexy', 'usa', 'house', 'american',
                       'party', 'favorite', 'favorite by this singer', 'seen live', 'electropop', 'singer-songwriter',
                       'happy', 'love', 'awesome', 'night', 'upbeat', 'funky', 'synthpop', 'fun', 'dance pop',
                       'best song ever', 'gorgeous', 'female vocal', 'pop-rock', 'love at first listen', 'english',
                       'love it', 'personal favourites', 'all time faves', 'vocalization', 'all the best',
                       'best songs of the 00s', 'dancemania', 'umpa umpa', 'welcome to the club', 'eletronic',
                       'sublime', 'dance all night', 'favourite songs', 'funky house', 'evening', 'the word night',
                       'songs of day and night', 'influential', 'summer 2009', 'female singer songwriter', 'attitude',
                       'current favorites', 'gay anthem', 'divas', 'stuff i dance to', 'dance remix', 'comeback',
                       'sleek', 'simply amazing', 'one of my favorite songs', 'fall 2009', 'teh sex', 'perfeita',
                       'nightlife', 'luxo', 'it is party time', 'amo', 'critically acclaimed song',
                       'i wish i could make a video for this', 'likeit', '08 gems', 'flat beat', 'eurocajon',
                       'folderland', 'eurocajon23', 'maravilhosa', 'move to this', 'hay hay hay',
                       'i want to be independent listening to', 'web-found', '124 bpm', 'the word life',
                       'the word into', 'the word nightlife', 'bluk track', 'energ', 'poderosa', '3 and a half stars',
                       'was zum discodancen', 'bring ya to the brink', 'rollo vuitantes', 'my house is on fire',
                       'mike andrews sex']
        self.assertEqual(tags, result_tags)

        # TODO: Test exceptions
