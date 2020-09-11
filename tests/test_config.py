import logging
import unittest

import config.config as cnfg


class TestConfig(unittest.TestCase):

    def test_set_up_logging_basic_config(self):
        # cnfg.set_up_logging_basic_config()
        logging.basicConfig(filename='D:\\plum_music\\logs\\plum_main.log',
                            format="%(name)s: %(levelname)s %(asctime)s\n\t%(message)s",
                            datefmt='%Y-%m-%d %H:%M',
                            filemode='w')
        logger = logging.getLogger(__name__)
        logger.info(f"Test info log 1")
